import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os

# Download required resources with error handling
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Download punkt_tab specifically
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab', quiet=True)
    except:
        print("punkt_tab not available. Using fallback tokenization.")

def clean_text(text):
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_and_remove_stopwords(text):
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return " ".join(filtered_tokens)

def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def preprocess_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    cleaned = clean_text(content)
    tokenized = tokenize_and_remove_stopwords(cleaned)
    return chunk_text(tokenized)

def process_all():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    changi_path = os.path.join(base_dir, 'data', 'changi_content.txt')
    jewel_path = os.path.join(base_dir, 'data', 'jewel_content.txt')
    
    changi_chunks = preprocess_file(changi_path)
    jewel_chunks = preprocess_file(jewel_path)
    return changi_chunks + jewel_chunks