import os
import requests
from bs4 import BeautifulSoup
import re

def scrape_changi():
    url = "https://www.changiairport.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove scripts/styles
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get clean text
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def scrape_jewel():
    url = "https://www.jewelchangiairport.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove scripts/styles
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get clean text
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def save_content():
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    os.makedirs(data_dir, exist_ok=True)
    
    changi = scrape_changi()
    jewel = scrape_jewel()
    
    changi_path = os.path.join(data_dir, 'changi_content.txt')
    jewel_path = os.path.join(data_dir, 'jewel_content.txt')
    
    with open(changi_path, 'w', encoding='utf-8') as f:
        f.write(changi)
    
    with open(jewel_path, 'w', encoding='utf-8') as f:
        f.write(jewel)

if __name__ == "__main__":
    save_content()