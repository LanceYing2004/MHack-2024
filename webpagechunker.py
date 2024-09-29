import requests
from bs4 import BeautifulSoup

# Fetch the webpage
url = 'https://discordpy.readthedocs.io/en/stable/api.html'
response = requests.get(url)
webpage_content = response.content

# Parse the webpage
soup = BeautifulSoup(webpage_content, 'html.parser')


def extract_sections(soup):
    sections = []
    current_section = {}
    
    for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
        if tag.name in ['h1', 'h2', 'h3']:  # If it's a header tag
            if current_section:  # If there's already a section, store it
                sections.append(current_section)
            # Start a new section
            current_section = {'header': tag.get_text(), 'content': ''}
        elif tag.name == 'p':  # If it's a paragraph, add it to the current section
            current_section['content'] += tag.get_text() + "\n"
    
    if current_section:  # Append the last section
        sections.append(current_section)
    
    return sections

# Extract sections from the webpage
sections = extract_sections(soup)

# Print the sections
for section in sections:
    print(f"Header: {section['header']}")
    print(f"Content: {section['content'][:100]}...")  # Preview the content

def merge_small_sections(sections, min_length=500):
    merged_sections = []
    current_chunk = ''
    current_header = ''

    for section in sections:
        content = section['header'] + "\n" + section['content']
        if len(current_chunk) + len(content) < min_length:
            current_chunk += content + "\n"
        else:
            merged_sections.append({'header': current_header.strip(), 'content': current_chunk.strip()})
            current_chunk = content
            current_header = section['header']
    
    if current_chunk:
        merged_sections.append({'header': current_header.strip(), 'content': current_chunk.strip()})

    return merged_sections

# Merge small sections if necessary
merged_sections = merge_small_sections(sections, min_length=500)

# Preview the merged sections
for section in merged_sections:
    print(f"Header: {section['header']}")
    print(f"Content: {section['content'][:100]}...")  # Preview the content
