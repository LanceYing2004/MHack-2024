import os
import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
import re
import json
import torch
import ollama
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

# Function to convert PDF to text and append to vault.txt
def convert_pdf_to_text():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        base_directory = os.path.join("local-rag", "text_parse")
        file_name = os.path.basename(file_path)
        output_file_name = os.path.splitext(file_name)[0] + ".txt"
        file_output_path = os.path.join(base_directory, output_file_name)

        if not os.path.exists(base_directory):
            os.makedirs(base_directory)
            print(f"Directory '{base_directory}' created.")

        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                if page.extract_text():
                    text += page.extract_text() + " "

            text = re.sub(r'\s+', ' ', text).strip()
            sentences = re.split(r'(?<=[.!?]) +', text)
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 < 1000:
                    current_chunk += (sentence + " ").strip()
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:
                chunks.append(current_chunk)

            with open(os.path.join("local-rag", "temp.txt"), "w", encoding="utf-8") as temp_file:
                temp_file.write(output_file_name + "\n")
                for chunk in chunks:
                    temp_file.write(chunk.strip() + "\n")
            
            with open(os.path.join("local-rag", "vault.txt"), "a", encoding="utf-8") as vault_file:
                vault_file.write("\n")
                for chunk in chunks:
                    vault_file.write(chunk.strip() + "\n")

            if not os.path.exists(file_output_path):
                with open(file_output_path, "w", encoding="utf-8") as f:
                    for chunk in chunks:
                        f.write(chunk.strip() + "\n")
                    f.write("====================NOT FINISHED====================\n")
                print(f"File '{file_output_path}' created with NOT FINISHED flag at the end.")
            else:
                print(f"File '{file_output_path}' already exists.")

            print(f"PDF content appended to vault.txt with each chunk on a separate line.")
            # Call the second part after the PDF conversion is done

        input_value = input("Enter your question:")
        process_text_files(input_value)

# Function to upload a text file and append to vault.txt
def upload_txtfile():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        # Define the base directory
        base_directory = os.path.join("local-rag", "text_parse")

        # Get the file name without the directory and extension
        file_name = os.path.basename(file_path)
        output_file_name = os.path.splitext(file_name)[0] + ".txt"  # Convert PDF filename to .txt


        # Construct the output file path in the base directory
        file_output_path = os.path.join(base_directory, output_file_name)

        # Create base directory if it doesn't exist
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)
            print(f"Directory '{base_directory}' created.")

            
        with open(file_path, 'r', encoding="utf-8") as txt_file:
            text = txt_file.read()
            
            # Normalize whitespace and clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split text into chunks by sentences, respecting a maximum chunk size
            sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                # Check if the current sentence plus the current chunk exceeds the limit
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 for the space
                    current_chunk += (sentence + " ").strip()
                else:
                    # When the chunk exceeds 1000 characters, store it and start a new one
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:  # Don't forget the last chunk!
                chunks.append(current_chunk)
            
            # Clear temp.txt and write the new content
            with open(os.path.join("local-rag", "temp.txt"), "w", encoding="utf-8") as temp_file:
                temp_file.write(output_file_name + "\n")  # Write the output file name as the first line
                for chunk in chunks:
                    # Write each chunk to its own line
                    temp_file.write(chunk.strip() + "\n")  # Each chunk on a new line
            
            with open(os.path.join("local-rag", "vault.txt"), "a", encoding="utf-8") as vault_file:
                vault_file.write("\n")  # Add a new line to separate content
                for chunk in chunks:
                    # Write each chunk to its own line
                    vault_file.write(chunk.strip() + "\n")  # Two newlines to separate chunks
            
            # Create the file in the directory if it doesn't exist
            if not os.path.exists(file_output_path):
                with open(file_output_path, "w") as f:
                    f.write("")  # Create an empty file
                    f.write("====================NOT FINISHED====================\n")
                print(f"File '{file_output_path}' created with NOT FINISHED flag at the end.")
            else:
                print(f"File '{file_output_path}' already exists.")
                
            print(f"Text file content appended to vault.txt with each chunk on a separate line.")

            input_value = input("Enter your question:")
            process_text_files(input_value)
    else:
        print("No file selected.")        

# Function to upload a JSON file and append to vault.txt
def upload_jsonfile():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        
        # Define the base directory
        base_directory = os.path.join("local-rag", "text_parse")

        # Get the file name without the directory and extension
        file_name = os.path.basename(file_path)
        output_file_name = os.path.splitext(file_name)[0] + ".txt"  # Convert PDF filename to .txt


        # Construct the output file path in the base directory
        file_output_path = os.path.join(base_directory, output_file_name)
        
        # Create base directory if it doesn't exist
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)
            print(f"Directory '{base_directory}' created.")
    
        
        
        
        with open(file_path, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
            
            # Flatten the JSON data into a single string
            text = json.dumps(data, ensure_ascii=False)
            
            # Normalize whitespace and clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split text into chunks by sentences, respecting a maximum chunk size
            sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                # Check if the current sentence plus the current chunk exceeds the limit
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 for the space
                    current_chunk += (sentence + " ").strip()
                else:
                    # When the chunk exceeds 1000 characters, store it and start a new one
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:  # Don't forget the last chunk!
                chunks.append(current_chunk)
            
            # Clear temp.txt and write the new content
            with open(os.path.join("local-rag", "temp.txt"), "w", encoding="utf-8") as temp_file:
                temp_file.write(output_file_name + "\n")  # Write the output file name as the first line
                for chunk in chunks:
                    # Write each chunk to its own line
                    temp_file.write(chunk.strip() + "\n")  # Each chunk on a new line
            
            with open(os.path.join("local-rag", "vault.txt"), "a", encoding="utf-8") as vault_file:
                vault_file.write("\n")  # Add a new line to separate content
                for chunk in chunks:
                    # Write each chunk to its own line
                    vault_file.write(chunk.strip() + "\n")  # Two newlines to separate chunks
                    
            if not os.path.exists(file_output_path):
                with open(file_output_path, "w", encoding="utf-8") as f:
                    for chunk in chunks:
                        f.write(chunk.strip() + "\n")  # Each chunk on a new line
                    f.write("====================NOT FINISHED====================\n")
                print(f"File '{file_output_path}' created with NOT FINISHED flag at the end.")
            else:
                print(f"File '{file_output_path}' already exists.")
            

            
            print(f"JSON file content appended to vault.txt with each chunk on a separate line.")
            
            input_value = input("Enter your question:")
            process_text_files(input_value)

def summarize():
    summary_window = tk.Toplevel(root)
    summary_window.title("Text Summarizer")
    summary_window.geometry("400x200")

    # Create a label for the window
    label = tk.Label(summary_window, text="Choose an option to summarize text:")
    label.pack(pady=10)

    # Create two buttons: one for uploading a .txt file, and one for pasting text directly
    upload_button = tk.Button(summary_window, text="Upload from .txt File", command=summarize_from_file)
    upload_button.pack(pady=5)

    paste_button = tk.Button(summary_window, text="Paste your text", command=lambda: open_paste_window(summary_window))
    paste_button.pack(pady=5)
    
# Function to upload a .txt file and summarize
def summarize_from_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        # Define the base directory where the file will be saved
        base_directory = os.path.join("local-rag", "text_sum")
        
        file_name = os.path.basename(file_path)

        # Create the directory if it doesn't exist
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)
            print(f"Directory '{base_directory}' created.")
        
        summary_content = []
        if os.path.exists(file_name):
            with open(file_name, "r", encoding='utf-8') as sum_file:
                summary_content = sum_file.readlines()
        
        summary_embeddings = []
        for content in summary_content:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
            summary_embeddings.append(response["embedding"])

        summary_embeddings_tensor = torch.tensor(summary_embeddings)
        print("Embeddings for each line in the vault:")
        print(summary_embeddings_tensor)

        conversation_history = []
        system_message = "You are a helpful assistant that is an expert at summarizing the text from a given document"
        user_input = "Summarize this paragraph"

        response = ollama_chat(user_input, system_message, summary_embeddings_tensor, summary_content, args.model, conversation_history)

        messagebox.showinfo("Summary", response)  # Replace with actual summarizing logic
    else:
        messagebox.showerror("Error", "No file selected!")

# Function to open a window for pasting text and summarizing
def open_paste_window(parent_window):
    # Create a new window for pasting text
    paste_window = tk.Toplevel(parent_window)
    paste_window.title("Paste Your Text")
    paste_window.geometry("400x300")

    # Create a label and text box for the pasted text
    label = tk.Label(paste_window, text="Paste your text below:")
    label.pack(pady=5)

    input_textbox = tk.Text(paste_window, height=8, width=40)
    input_textbox.pack(pady=5)

    # Function to handle the "Submit" button click
    def submit_text():
        pasted_text = input_textbox.get("1.0", tk.END).strip()
        if pasted_text:
            
            
            system_message = "You are a helpful assistant that is an expert at summarizing the text from a given document"
            user_input = "Summarize this paragraph:"
            new_value = user_input + pasted_text
            messages = [
                (
                    "system",
                    system_message,
                ),
                ("human", new_value),
            ]        
            response = client.chat.completions.create(model=args.model, messages=messages)

            response_value = response.choices[0].message.content


            messagebox.showinfo("Summary", response_value)  # Replace with actual summarizing logic
            paste_window.destroy()  # Close the window
        else:
            messagebox.showerror("Error", "No text entered!")

    # Add Submit and Cancel buttons
    submit_button = tk.Button(paste_window, text="Submit", command=submit_text)
    submit_button.pack(side=tk.LEFT, padx=10, pady=10)

    cancel_button = tk.Button(paste_window, text="Cancel", command=paste_window.destroy)
    cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)


# Function to get relevant context from the vault based on user input
def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:
        return []
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    top_k = min(top_k, len(cos_scores))
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    relevant_context = [vault_content[idx].strip() for idx in top_indices]
    return relevant_context

# Function to interact with the Ollama model
def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history):
    relevant_context = get_relevant_context(user_input, vault_embeddings, vault_content, top_k=3)
    if relevant_context:
        context_str = "\n".join(relevant_context)
        print("Context Pulled from Documents: \n\n" + CYAN + context_str + RESET_COLOR)
    else:
        print(CYAN + "No relevant context found." + RESET_COLOR)
    
    user_input_with_context = user_input
    if relevant_context:
        user_input_with_context = context_str + "\n\n" + user_input
    
    conversation_history.append({"role": "user", "content": user_input_with_context})
    messages = [{"role": "system", "content": system_message}, *conversation_history]
    
    response = client.chat.completions.create(model=ollama_model, messages=messages)
    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
    
    return response.choices[0].message.content

# Function to process text files, check for NOT FINISHED flag, and compute embeddings
def process_text_files(user_input):
    text_parse_directory = os.path.join("local-rag", "text_parse")
    temp_file_path = os.path.join("local-rag", "temp.txt")

    if not os.path.exists(text_parse_directory):
        print(f"Directory '{text_parse_directory}' does not exist.")
        return False

    if not os.path.exists(temp_file_path):
        print("temp.txt does not exist.")
        return False
    
    with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
        first_line = temp_file.readline().strip()

    text_files = [f for f in os.listdir(text_parse_directory) if f.endswith('.txt')]
    
    if f"{first_line}" not in text_files:
        print(f"No matching file found for '{first_line}.txt' in text_parse directory.")
        return False

    file_path = os.path.join(text_parse_directory, f"{first_line}")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    lines = [line.strip() for line in lines]

    if len(lines) >= 2 and lines[-1] == "====================NOT FINISHED====================":
        print(f"'{first_line}' contains the 'NOT FINISHED' flag. Computing embeddings.")

        vault_content = []
        if os.path.exists(temp_file_path):
            with open(temp_file_path, "r", encoding='utf-8') as vault_file:
                vault_content = vault_file.readlines()

        vault_embeddings = []
        for content in vault_content:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
            vault_embeddings.append(response["embedding"])

        vault_embeddings_tensor = torch.tensor(vault_embeddings)
        print("Embeddings for each line in the vault:")
        print(vault_embeddings_tensor)
        
        with open(os.path.join(text_parse_directory, f"{first_line}_embedding.pt"), "wb") as tensor_file:
            torch.save(vault_embeddings_tensor, tensor_file)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines[:-1])

    else:
        print(f"'{first_line}' does not contain the 'NOT FINISHED' flag or is already complete. Loading tensor if it exists.")

        tensor_file_path = os.path.join(text_parse_directory, f"{first_line}_embedding.pt")
        if os.path.exists(tensor_file_path):
            vault_embeddings_tensor = torch.load(tensor_file_path)
            print("Loaded Vault Embedding Tensor:")
            print(vault_embeddings_tensor)

            vault_content = []
            if os.path.exists(temp_file_path):
                with open(temp_file_path, "r", encoding='utf-8') as vault_file:
                    vault_content = vault_file.readlines()

    conversation_history = []
    system_message = "You are a helpful assistant that is an expert at extracting the most useful information from a given text"
    response = ollama_chat(user_input, system_message, vault_embeddings_tensor, vault_content, args.model, conversation_history)
    
    print (response)

    return response

# Create the main window
root = tk.Tk()
root.title("Upload .pdf, .txt, or .json")

# Create a button to open the file dialog for PDF
pdf_button = tk.Button(root, text="Upload PDF", command=convert_pdf_to_text)
pdf_button.pack(pady=15)

# Create a button to open the file dialog for text file
txt_button = tk.Button(root, text="Upload Text File", command=upload_txtfile)
txt_button.pack(pady=15)

# Create a button to open the file dialog for JSON file
json_button = tk.Button(root, text="Upload JSON File", command=upload_jsonfile)
json_button.pack(pady=15)

# Create a button to open the summerizer
json_button = tk.Button(root, text="Summarize This!", command=summarize)
json_button.pack(pady=15)

# Configuration for the Ollama API client
client = OpenAI(base_url='http://localhost:11434/v1', api_key='llama3')

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Ollama Chat")
parser.add_argument("--model", default="llama3", help="Ollama model to use (default: llama3)")
args = parser.parse_args()

# Run the main event loop
root.mainloop()
