import os
import csv
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000, chunk_overlap=1000)
    chunks = splitter.split_text(text)
    return chunks


def get_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  # type: ignore
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context.
    If the answer is not in the context, say "answer is not available in the context".
    
    Context: {context}
    Question: {question}

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro",
                                   client=None,
                                   temperature=0.3)
    prompt = PromptTemplate(template=prompt_template,
                            input_variables=["context", "question"])
    chain = load_qa_chain(llm=model, chain_type="stuff", prompt=prompt)
    return chain


def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "Upload some PDFs and ask me a question"}]


def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001")  # type: ignore

    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    context = "\n".join([doc.page_content for doc in docs])
    response = chain(
        {"input_documents": docs, "context": context, "question": user_question},
        return_only_outputs=True)

    return response['output_text']


def save_user_info(name, phone, email):
    file_exists = os.path.isfile('user_info.csv')
    with open('user_info.csv', mode='a', newline='') as file:
        fieldnames = ['Name', 'Phone', 'Email']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({'Name': name, 'Phone': phone, 'Email': email})


def main():
    st.set_page_config(
        page_title="Chat with PDFs",
        page_icon="📄",
        layout="wide"
    )

    with st.sidebar:
        st.title("Menu")
        pdf_docs = st.file_uploader(
            "Upload your PDF Files and Click on the Submit & Process Button",
            accept_multiple_files=True)
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Done")

    st.title("Chat with PDF files using Gemini 🙋‍♂️")
    st.write("Welcome to the chat!")
    st.sidebar.button("Clear Chat History", on_click=clear_chat_history)

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": "Upload some PDFs and ask me a question"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f"**{message['role'].capitalize()}:** {message['content']}")

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"**User:** {prompt}")

        if "call me" in prompt.lower():
            st.session_state.collecting_info = True

        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = user_input(prompt)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.markdown(f"**Assistant:** {response}")

    if "collecting_info" in st.session_state and st.session_state.collecting_info:
        st.subheader("Please provide your contact details")
        with st.form(key="contact_form"):
            name = st.text_input("Name")
            phone = st.text_input("Phone Number")
            email = st.text_input("Email Address")
            submit_button = st.form_submit_button("Submit")

            if submit_button:
                save_user_info(name, phone, email)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Thank you, {name}. We will contact you at {phone} or {email}."
                })
                st.session_state.collecting_info = False


if __name__ == "__main__":
    main()
