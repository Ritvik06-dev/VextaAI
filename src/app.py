import streamlit as st
import requests
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY")
PAGEINDEX_BASE_URL = "https://api.pageindex.ai"

st.set_page_config(
    page_title = "VextaAI - Personal Research Assistant",
    page_icon = "🤖",
    layout="wide"
)

#app title and despcription
st.title("VextaAI - Personal Research Assistant")
st.markdown("Welcome to VextaAI! This is your personal research assistant that helps you manage and query your documents using the power of PageIndex. You can ingest documents, ask questions, and get answers based on the content of your indexed files.")
st.divider()

def get_documents():
    #fet all indexed documents from the PageIndex API
    headers = {"api_key": PAGEINDEX_API_KEY}
    response = requests.get(f"{PAGEINDEX_BASE_URL}/docs", headers=headers)  

    if response.status_code == 200:
        data = response.json()
        return data.get("documents", [])
    return []

def ask_question(doc_id, question):
    #send question to PageIndex chat API
    headers = {"api_key": PAGEINDEX_API_KEY, "Content-Type": "application/json"}
    payload = {"messages": [{"role": "user", "content": question}], "doc_id": doc_id}
    response = requests.post(f"{PAGEINDEX_BASE_URL}/chat/completions/", headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return f"Error: {response.text}"

#Sidebar - document selector
st.sidebar.header("Your Documents")
documents = get_documents()

if not documents:
    st.sidebar.warning("No documents found. Please ingest some documents first.")
    selected_doc_id = None
else:
    #create a dropdown to select a document
    doc_name = [doc["name"] for doc in documents]
    selected_name  = st.sidebar.selectbox("Select a document to query:", doc_name)
    selected_doc_id = next((doc["id"] for doc in documents if doc["name"] == selected_name), None)
    st.sidebar.success(f"Selected document: {selected_name}")

#file uploader section
st.sidebar.divider()
st.sidebar.header("Ingest New Document")
uploaded_file = st.sidebar.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file:
    if st.sidebar.button("Ingest Document"):
        with st.spinner("Uploading to PageIndex..."):
            headers = {"api_key": PAGEINDEX_API_KEY}
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            response = requests.post(f"{PAGEINDEX_BASE_URL}/doc/", headers=headers, files=files)
            if response.status_code == 200:
                st.sidebar.success(f"Successfully ingested {uploaded_file.name}. Please select it from the dropdown to query.")
                st.rerun()
            else:
                st.sidebar.error(f"Failed to ingest {uploaded_file.name}: {response.status_code} - {response.text}")

#main chat area
st.subheader("Chat with your documents")

#Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#Handle new user input
if prompt := st.chat_input("Ask anything about your document..."):
    if not selected_doc_id:
        st.error("Please select a document from the sidebar to start chatting.")
    else:
        #add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        #get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Assistant is thinking..."):
                answer = ask_question(selected_doc_id, prompt)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})