# chatbot.py
# Install: pip install transformers gradio
# Run:     python chatbot.py

from transformers import pipeline, Conversation
import gradio as gr

# ── Load model ────────────────────────────────────────────────────────────────
chatbot = pipeline("conversational", model="facebook/blenderbot-400M-distill")

# ── Test a two-turn conversation in the console ───────────────────────────────
conversation = Conversation("Hi, how are you?")
conversation = chatbot(conversation)
print(conversation)

conversation.add_user_input("What do you like to do for fun?")
conversation = chatbot(conversation)
print(conversation)

# ── Gradio interface ──────────────────────────────────────────────────────────
message_list  = []
response_list = []

def mini_chatbot(message, history):
    conversation = Conversation(
        text=message,
        past_user_inputs=message_list,
        generated_responses=response_list,
    )
    conversation = chatbot(conversation)

    message_list.append(message)
    response_list.append(conversation.generated_responses[-1])

    return conversation.generated_responses[-1]


demo_chatbot = gr.ChatInterface(
    mini_chatbot,
    title="BlenderBot Chatbot",
    description="A friendly chatbot powered by facebook/blenderbot-400M-distill.",
)

demo_chatbot.launch()
