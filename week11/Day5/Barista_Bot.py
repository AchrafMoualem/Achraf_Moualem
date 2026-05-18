# =============================================================================
# BaristaBot — LangGraph Cafe Ordering System (single file)
# =============================================================================


import os


from collections.abc import Iterable
from random import randint
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pprint import pprint

from langchain_core.messages.ai import AIMessage
from langchain_core.messages.tool import ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# =============================================================================
# STATE SCHEMA
# =============================================================================

class OrderState(TypedDict):
    """State representing the customer's order conversation."""
    messages: Annotated[list, add_messages]  # conversation history (appended, not replaced)
    order: list[str]                          # items added so far
    finished: bool                            # True once place_order is called

# =============================================================================
# SYSTEM PROMPT & WELCOME MESSAGE
# =============================================================================

BARISTABOT_SYSINT = (
    "system",
    "You are a BaristaBot, an interactive cafe ordering system. A human will talk to you about the "
    "available products you have and you will answer any questions about menu items (and only about "
    "menu items - no off-topic discussion, but you can chat about the products and their history). "
    "The customer will place an order for 1 or more items from the menu, which you will structure "
    "and send to the ordering system after confirming the order with the human. "
    "\n\n"
    "Add items to the customer's order with add_to_order, and reset the order with clear_order. "
    "To see the contents of the order so far, call get_order (this is shown to you, not the user). "
    "Always confirm_order with the user (double-check) before calling place_order. Calling confirm_order will "
    "display the order items to the user and returns their response to seeing the list. Their response may contain modifications. "
    "Always verify and respond with drink and modifier names from the MENU before adding them to the order. "
    "If you are unsure a drink or modifier matches those on the MENU, ask a question to clarify or redirect. "
    "You only have the modifiers listed on the menu. "
    "Once the customer has finished ordering items, Call confirm_order to ensure it is correct then make "
    "any necessary updates and then call place_order. Once place_order has returned, thank the user and "
    "say goodbye!",
)

WELCOME_MSG = "Welcome to the BaristaBot cafe. Type `q` to quit. How may I serve you today?"

# =============================================================================
# LLM
# =============================================================================

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-latest")

# =============================================================================
# TOOLS — STATELESS (auto-executed by ToolNode)
# =============================================================================

@tool
def get_menu() -> str:
    """Provide the latest up-to-date menu."""
    return """
    MENU:
    Coffee Drinks:
      Espresso, Americano, Cold Brew

    Coffee Drinks with Milk:
      Latte, Cappuccino, Cortado, Macchiato, Mocha, Flat White

    Tea Drinks:
      English Breakfast Tea, Green Tea, Earl Grey

    Tea Drinks with Milk:
      Chai Latte, Matcha Latte, London Fog

    Other Drinks:
      Steamer, Hot Chocolate

    Modifiers:
      Milk options: Whole, 2%, Oat, Almond, 2% Lactose Free; Default: Whole
      Espresso shots: Single, Double, Triple, Quadruple; Default: Double
      Caffeine: Decaf, Regular; Default: Regular
      Hot-Iced: Hot, Iced; Default: Hot
      Sweeteners (one or more): vanilla sweetener, hazelnut sweetener,
        caramel sauce, chocolate sauce, sugar free vanilla sweetener
      Special requests: extra hot, one pump, half caff, extra foam, etc.

    Notes:
      "dirty" = add a shot of espresso to a drink that doesn't normally have it.
      "Regular milk" = whole milk.
      "Sweetened" = add regular sugar (not a sweetener).
      Soy milk is OUT OF STOCK today.
    """

# =============================================================================
# TOOLS — STATEFUL (handled by order_node, stubs only)
# =============================================================================

@tool
def add_to_order(drink: str, modifiers: Iterable[str]) -> str:
    """Adds the specified drink to the customer's order, including any modifiers.

    Returns:
        The updated order in progress.
    """

@tool
def confirm_order() -> str:
    """Asks the customer if the order is correct.

    Returns:
        The user's free-text response.
    """

@tool
def get_order() -> str:
    """Returns the user's order so far. One item per line."""

@tool
def clear_order():
    """Removes all items from the user's order."""

@tool
def place_order() -> int:
    """Sends the order to the barista for fulfillment.

    Returns:
        The estimated number of minutes until the order is ready.
    """

# =============================================================================
# TOOL NODES
# =============================================================================

auto_tools  = [get_menu]
order_tools = [add_to_order, confirm_order, get_order, clear_order, place_order]
all_tools   = auto_tools + order_tools

tool_node   = ToolNode(auto_tools)                  # runs get_menu automatically
llm_with_tools = llm.bind_tools(all_tools)          # LLM knows about everything

# =============================================================================
# NODES
# =============================================================================

def chatbot_node(state: OrderState) -> OrderState:
    """Core chatbot node. Sends full message history to the LLM."""
    defaults = {"order": [], "finished": False}

    if state["messages"]:
        new_output = llm_with_tools.invoke([BARISTABOT_SYSINT] + state["messages"])
    else:
        new_output = AIMessage(content=WELCOME_MSG)

    return defaults | state | {"messages": [new_output]}


def human_node(state: OrderState) -> OrderState:
    """Display the last model message and collect user input."""
    last_msg = state["messages"][-1]
    print("Model:", last_msg.content)

    user_input = input("User: ")

    if user_input.strip().lower() in {"q", "quit", "exit", "goodbye"}:
        state["finished"] = True

    return state | {"messages": [("user", user_input)]}


def order_node(state: OrderState) -> OrderState:
    """Handle all stateful ordering tool calls and update the order in state."""
    tool_msg      = state["messages"][-1]   # last message contains tool_calls
    order         = list(state.get("order", []))
    outbound_msgs = []
    order_placed  = False

    for tool_call in tool_msg.tool_calls:
        name = tool_call["name"]

        if name == "add_to_order":
            modifiers    = tool_call["args"].get("modifiers", [])
            modifier_str = ", ".join(modifiers) if modifiers else "no modifiers"
            order.append(f'{tool_call["args"]["drink"]} ({modifier_str})')
            response = "\n".join(order)

        elif name == "confirm_order":
            print("\nYour order:")
            if not order:
                print("  (no items)")
            for drink in order:
                print(f"  {drink}")
            response = input("Is this correct? ")

        elif name == "get_order":
            response = "\n".join(order) if order else "(no order)"

        elif name == "clear_order":
            order.clear()
            response = "Order cleared."

        elif name == "place_order":
            order_text = "\n".join(order)
            print("\nSending order to kitchen!")
            print(order_text)
            order_placed = True
            response = randint(1, 5)   # ETA in minutes

        else:
            raise NotImplementedError(f"Unknown tool call: {name}")

        outbound_msgs.append(
            ToolMessage(
                content=str(response),
                name=name,
                tool_call_id=tool_call["id"],
            )
        )

    return {"messages": outbound_msgs, "order": order, "finished": order_placed}

# =============================================================================
# ROUTING FUNCTIONS (conditional edges)
# =============================================================================

def maybe_route_to_tools(state: OrderState) -> str:
    """Route chatbot output to: tools, ordering, human, or END."""
    if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found: {state}")

    msg = msgs[-1]

    if state.get("finished", False):
        return END

    if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        # Check if any call targets an auto tool (ToolNode)
        if any(tc["name"] in tool_node.tools_by_name for tc in msg.tool_calls):
            return "tools"
        return "ordering"

    return "human"


def maybe_exit_human_node(state: OrderState) -> Literal["chatbot", "__end__"]:
    """Route human output back to chatbot, or exit if user is done."""
    if state.get("finished", False):
        return END
    return "chatbot"

# =============================================================================
# BUILD GRAPH
# =============================================================================

graph_builder = StateGraph(OrderState)

graph_builder.add_node("chatbot",  chatbot_node)
graph_builder.add_node("human",    human_node)
graph_builder.add_node("tools",    tool_node)
graph_builder.add_node("ordering", order_node)

graph_builder.add_edge(START, "chatbot")

# chatbot → tools | ordering | human | END
graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
# human → chatbot | END
graph_builder.add_conditional_edges("human",   maybe_exit_human_node)
# Both tool nodes always return to chatbot
graph_builder.add_edge("tools",    "chatbot")
graph_builder.add_edge("ordering", "chatbot")

graph = graph_builder.compile()

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  BaristaBot — type 'q' at any time to quit")
    print("="*60 + "\n")

    config = {"recursion_limit": 100}
    final_state = graph.invoke({"messages": []}, config)

    print("\n--- Session complete ---")
    print(f"Final order: {final_state.get('order', [])}")