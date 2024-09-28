import os
import requests
from bs4 import BeautifulSoup

def download_webpages(urls, save_dir='webpages'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text and save it to a file
        filename = os.path.join(save_dir, url.split('/')[-1] + '.txt')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(soup.get_text(separator=' ', strip=True))
        print(f"Downloaded: {filename}")

# Example usage
urls = [
    'https://example.com',
    'https://www.iana.org/help/example-domains'
]
download_webpages(urls)

def load_documents_from_local_directory(directory='webpages'):
    docs = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                docs.append(f.read())
    return docs

def get_documents():
    return load_documents_from_local_directory()

# Usage in the main logic
if __name__ == "__main__":
    # Load documents from local files
    docs = get_documents()
    vectorStore = create_db(docs)
    chain = create_chain(vectorStore)

    # Initialize chat history
    chat_history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = process_chat(chain, user_input, chat_history)
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response))
        print("Assistant:", response)