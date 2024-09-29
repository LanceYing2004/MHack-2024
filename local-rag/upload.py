import os
import tkinter as tk
from tkinter import filedialog
import PyPDF2
import re
import json

# Function to convert PDF to text and append to vault.txt
def convert_pdf_to_text():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
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
        

        if os.path.exists(file_output_path):
            print(f"File '{file_output_path}' already exists.")
            return None

        
        
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            text = ''
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                if page.extract_text():
                    text += page.extract_text() + " "
            
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
                

        
            print(f"PDF content appended to vault.txt with each chunk on a separate line.")
    else:
        print("No file selected.")

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
        

        if os.path.exists(file_output_path):
            print(f"File '{file_output_path}' already exists.")
            return None

            
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
        

        if os.path.exists(file_output_path):
            print(f"File '{file_output_path}' already exists.")
            return None
        
        
        
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

# Create the main window
root = tk.Tk()
root.title("Upload .pdf, .txt, or .json")

# Create a button to open the file dialog for PDF
pdf_button = tk.Button(root, text="Upload PDF", command=convert_pdf_to_text)
pdf_button.pack(pady=10)

# Create a button to open the file dialog for text file
txt_button = tk.Button(root, text="Upload Text File", command=upload_txtfile)
txt_button.pack(pady=10)

# Create a button to open the file dialog for JSON file
json_button = tk.Button(root, text="Upload JSON File", command=upload_jsonfile)
json_button.pack(pady=10)

# Run the main event loop
root.mainloop()
