import torch
import ollama
import os
from openai import OpenAI
import argparse

# ANSI escape codes for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Function to open a file and return its contents as a string
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Function to get relevant context from the vault based on user input
def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:  # Check if the tensor has any elements
        return []
    # Encode the rewritten input
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
    # Compute cosine similarity between the input and vault embeddings
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    # Adjust top_k if it's greater than the number of available scores
    top_k = min(top_k, len(cos_scores))
    # Sort the scores and get the top-k indices
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    # Get the corresponding context from the vault
    relevant_context = [vault_content[idx].strip() for idx in top_indices]
    return relevant_context

# Function to interact with the Ollama model
def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history):
    # Get relevant context from the vault
    relevant_context = get_relevant_context(user_input, vault_embeddings, vault_content, top_k=3)
    if relevant_context:
        # Convert list to a single string with newlines between items
        context_str = "\n".join(relevant_context)
        print("Context Pulled from Documents: \n\n" + CYAN + context_str + RESET_COLOR)
    else:
        print(CYAN + "No relevant context found." + RESET_COLOR)
    
    # Prepare the user's input by concatenating it with the relevant context
    user_input_with_context = user_input
    if relevant_context:
        user_input_with_context = context_str + "\n\n" + user_input
    
    # Append the user's input to the conversation history
    conversation_history.append({"role": "user", "content": user_input_with_context})
    
    # Create a message history including the system message and the conversation history
    messages = [
        {"role": "system", "content": system_message},
        *conversation_history
    ]
    
    # Send the completion request to the Ollama model
    response = client.chat.completions.create(
        model=ollama_model,
        messages=messages
    )
    
    # Append the model's response to the conversation history
    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
    
    # Return the content of the response from the model
    return response.choices[0].message.content

def process_text_files(user_input):
    text_parse_directory = os.path.join("local-rag", "text_parse")
    temp_file_path = os.path.join("local-rag", "temp.txt")

    # Check if text_parse directory exists
    if not os.path.exists(text_parse_directory):
        print(f"Directory '{text_parse_directory}' does not exist.")
        return False

    # Check if temp.txt exists
    if not os.path.exists(temp_file_path):
        print("temp.txt does not exist.")
        return False
    
    # Read the first line of temp.txt
    with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
        first_line = temp_file.readline().strip()

    # Get all text files in the text_parse directory
    text_files = [f for f in os.listdir(text_parse_directory) if f.endswith('.txt')]
    
    # Check if the first line matches any of the text files
    if f"{first_line}" not in text_files:
        print(f"No matching file found for '{first_line}.txt' in text_parse directory.")
        return False

    # Proceed to check for the NOT FINISHED flag
    file_path = os.path.join(text_parse_directory, f"{first_line}")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()


    # Check if there are any lines after NOT FINISHED
    if lines[-2].strip() == "====================NOT FINISHED====================":
        print(f"'{first_line}' contains the 'NOT FINISHED' flag. Computing embeddings.")

        vault_content = []
        if os.path.exists(temp_file_path):
            with open(temp_file_path, "r", encoding='utf-8') as vault_file:
                vault_content = vault_file.readlines()


        # Generate embeddings for the vault content using Ollama
        vault_embeddings = []
        for content in vault_content:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
            vault_embeddings.append(response["embedding"])

        # Convert to tensor and print embeddings
        vault_embeddings_tensor = torch.tensor(vault_embeddings) 
        print("Embeddings for each line in the vault:")
        print(vault_embeddings_tensor)
        
        # Save the tensor result to a file or variable as needed
        with open(os.path.join(text_parse_directory, f"{first_line}_embedding.pt"), "wb") as tensor_file:
            torch.save(vault_embeddings_tensor, tensor_file)

        # Remove the NOT FINISHED line from the original file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines[:-1])  # Write back all lines except the NOT FINISHED line

    else:
        print(f"'{first_line}' does not contain the 'NOT FINISHED' flag or is already complete. Loading tensor if it exists.")

        # Try to load the tensor from the corresponding file
        tensor_file_path = os.path.join(text_parse_directory, f"{first_line}_embedding.pt")
        if os.path.exists(tensor_file_path):
            vault_embeddings_tensor = torch.load(tensor_file_path)
            print("Loaded Vault Embedding Tensor:")
            print(vault_embeddings_tensor)

            vault_content = []
            
            if os.path.exists(temp_file_path):
                with open(temp_file_path, "r", encoding='utf-8') as vault_file:
                    vault_content = vault_file.readlines()

        else:
            print(f"No tensor file found for '{text_files}'.")

    
    
     # Conversation loop
    conversation_history = []
    system_message = "You are a helpful assistant that is an expert at extracting the most useful information from a given text"

    response = ollama_chat(user_input, system_message, vault_embeddings_tensor, vault_content, args.model, conversation_history)
    
    return response

    


    # # Read each file in the text_parse directory and check for the NOT FINISHED flag
    # for txt_file in text_files:
    #     file_path = os.path.join(text_parse_directory, txt_file)
    #     with open(file_path, 'r', encoding='utf-8') as f:
    #         lines = f.readlines()
    #         # Check if the last line contains the "NOT FINISHED" flag
    #         if lines and lines[-1].strip() == "==========NOT FINISHED==========":
    #             print(f"'{txt_file}' contains the 'NOT FINISHED' flag. Proceeding to next step.")
    #             # Append the content of this file to the vault
    #             with open(temp_file_path, 'a', encoding='utf-8') as vault_file:
    #                 vault_file.write('\n'.join(lines[:-1]) + '\n')  # Append content without the last flag line
    #         else:
    #             print(f"'{txt_file}' does not contain the 'NOT FINISHED' flag. Skipping.")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Ollama Chat")
parser.add_argument("--model", default="llama3", help="Ollama model to use (default: llama3)")
args = parser.parse_args()

# Configuration for the Ollama API client
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='llama3'
)

if __name__ == "__main__":
    print(process_text_files("tell me about iterators"))


