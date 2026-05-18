from langchain.memory import ConversationBufferMemory

# Initialize the memory
memory = ConversationBufferMemory()

# First interaction
memory.save_context(
    {"input": "Hello, how are you?"},
    {"output": "I'm fine, thank you. How can I assist you today?"}
)

# Follow-up message
memory.save_context(
    {"input": "Tell me a joke."},
    {"output": "Why did the chicken cross the road? To get to the other side."}
)

# Retrieve the conversation history
conversation_history = memory.load_memory_variables({})

# Print the memory
print(conversation_history)
