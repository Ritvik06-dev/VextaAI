import os
import requests
from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY")
PAGEINDEX_BASE_URL = "https://api.pageindex.ai"

def get_documents():
    #set up headers for the API request
    headers = {"api_key": PAGEINDEX_API_KEY}

    #request list of all documents from the PageIndex API
    response = requests.get(f"{PAGEINDEX_BASE_URL}/docs", headers=headers)

    #check if the request was successful
    if response.status_code == 200:
        data = response.json()
        print(f"Raw API response: {data}")
        return data.get("documents", [])
    else:
        print(f"Failed to retrieve documents: {response.status_code} - {response.text}")
        return []
    
def ask_question(doc_id, question):
    #set up headers for the API request
    headers = {"api_key": PAGEINDEX_API_KEY, "Content-Type": "application/json"}

    payload = {
        "messages": [{"role": "user", "content": question}],
        "doc_id": doc_id
    }

    response = requests.post(f"{PAGEINDEX_BASE_URL}/chat/completions/", headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]  #return the answer from the API response
    else:
        print(f"Failed to ask question: {response.status_code} - {response.text}")
        return None
    
#main function to test the chat functionality
def main():
    print("Welcome to the Personal Research Assistant!")
    print("Retrieving documents from PageIndex...")

    #get all indexed documents
    docs = get_documents()

    if not docs:
        print("No documents found. Please ingest some documents first.")
        return
    
    #show the user their available documents
    print("Your indexed documents:")
    for i, doc in enumerate(docs):
        print(f"  {i + 1}. {doc['name']}") 

    #ask the user to select a document
    choice = int(input("Select a document by number: ")) - 1
    doc_id = docs[choice]["id"]
    doc_name = docs[choice]["name"]

    print(f"You selected: {doc_name}")
    print("Type 'quit' to exit\n")

    #start the chat loop
    while True:
        question = input("You: ")
        if question.lower() == "quit":
            print("Goodbye!")
            break

        if not question.strip():
            continue  

        print("Assistant is thinking...")
        answer = ask_question(doc_id, question)

        if answer:
            print(f"Assistant: {answer}\n")

if __name__ == "__main__":
    main()