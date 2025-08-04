# src/chatbot.py

import os
import faiss
import logging
import re
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from dotenv import load_dotenv
import time
import traceback

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChangiChatbot:
    def __init__(self):
        logger.info("🔧 Initializing ChangiChatbot...")

        # Corrected paths - use embeddings directory instead of data
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.index_path = os.path.join(root_dir, 'embeddings/vector_store/faiss_index.bin')
        self.chunks_path = os.path.join(root_dir, 'embeddings/vector_store/chunks.txt')
        
        logger.info(f"Looking for index at: {self.index_path}")
        logger.info(f"Looking for chunks at: {self.chunks_path}")

        # Verify files exist before loading models
        if not os.path.exists(self.index_path):
            logger.error(f"FAISS index file not found at {self.index_path}")
            raise FileNotFoundError(f"Index not found: {self.index_path}")
        if not os.path.exists(self.chunks_path):
            logger.error(f"Chunk file not found at {self.chunks_path}")
            raise FileNotFoundError(f"Chunks not found: {self.chunks_path}")

        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.qa_pipeline = pipeline('question-answering',
                                     model='deepset/roberta-base-squad2',
                                     tokenizer='deepset/roberta-base-squad2')

        self.vector_index = self.load_vector_index()
        self.text_chunks = self.load_text_chunks()
        self.domain_keywords = self.define_domain_keywords()

        logger.info("✅ ChangiChatbot initialized successfully")

    def load_vector_index(self):
        logger.info("Loading FAISS index...")
        return faiss.read_index(self.index_path)

    def load_text_chunks(self):
        logger.info("Loading text chunks...")
        with open(self.chunks_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]

    def define_domain_keywords(self):
        return {
            'dining': ['eat', 'dine', 'restaurant', 'food', 'cuisine', 'cafe', 'menu'],
            'attractions': ['attraction', 'visit', 'experience', 'fun', 'activities'],
            'rain_vortex': ['rain vortex', 'waterfall', 'hsbc', 'vortex'],
            'transport': ['transport', 'mrt', 'bus', 'taxi', 'directions', 'car', 'drive'],
            'services': ['wifi', 'luggage', 'storage', 'facilities', 'amenities', 'service']
        }

    def recognize_intent(self, query):
        lower_query = query.lower()
        for intent, keywords in self.domain_keywords.items():
            if any(kw in lower_query for kw in keywords):
                return intent
        return 'general'

    def get_relevant_chunks(self, query, top_k=5):
        query_embedding = self.embedder.encode([query])
        distances, indices = self.vector_index.search(query_embedding, top_k)
        return [self.text_chunks[i] for i in indices[0]]

    def generate_answer(self, query, context_chunks):
        # First try to find exact answer in context
        for idx, chunk in enumerate(context_chunks):
            try:
                result = self.qa_pipeline(question=query, context=chunk)
                if result['score'] > 0.35:
                    return result['answer']
            except Exception as err:
                logger.warning(f"QA failed on chunk {idx}: {err}")
        
        # Fallback to intent-based response
        return self.generative_fallback(query, context_chunks)

    def generative_fallback(self, query, context_chunks):
        context = " ".join(context_chunks[:2])
        intent = self.recognize_intent(query)

        if intent == 'dining':
            return f"🍽️ Jewel Changi offers diverse dining options across its levels. {context[:200]}...\n\nSee full list: https://www.changiairport.com/en/dine"
        elif intent == 'rain_vortex':
            return ("🌊 The Rain Vortex is the world's tallest indoor waterfall, standing at 40 meters tall. "
                    f"{context[:150]}...\n\nLight shows run daily from 7:30PM to 12:30AM. "
                    "Details: https://www.changiairport.com/en/attractions/rain-vortex.html")
        elif intent == 'transport':
            return ("🚗 Getting to Jewel Changi:\n"
                    "- MRT: Changi Airport Station (CG2)\n"
                    "- Bus: 24, 27, 34, 36, 53, 110\n"
                    "- Taxi: Available at all terminals\n"
                    "- Parking: Available at basement levels")
        elif intent == 'services':
            return (f"🔧 Services at Changi Airport include:\n"
                    f"- Luggage storage\n- Free WiFi\n- Currency exchange\n- Medical services\n\n{context[:200]}...")
        else:
            return f"ℹ️ Here's what I found about your query:\n\n{context[:250]}..."

    def _check_greetings(self, query):
        patterns = [r'\bhello\b', r'\bhi\b', r'\bhey\b', r'\bhelp\b', r'\bstart\b']
        if any(re.search(pat, query.lower()) for pat in patterns):
            return (
                "👋 Welcome to Changi Airport Assistant!\n\n"
                "I can help with information about:\n"
                "• Dining options in Jewel 🍽️\n"
                "• Attractions like the Rain Vortex 🌟\n"
                "• Transportation options 🚕\n"
                "• Services (luggage, WiFi, etc.) 💼\n\n"
                "What would you like to know today?"
            )
        return None

    def get_changi_info(self, query):
        try:
            logger.info(f"Processing query: '{query}'")
            
            # Handle greetings first
            greeting = self._check_greetings(query)
            if greeting:
                return greeting

            # Get relevant context
            context_chunks = self.get_relevant_chunks(query)
            if not context_chunks:
                return "🤖 I couldn't find relevant information. Try asking about dining, attractions, or services at Changi."
            
            # Generate and return answer
            return self.generate_answer(query, context_chunks)
            
        except Exception as e:
            logger.error(f"Error in get_changi_info: {e}\n{traceback.format_exc()}")
            return "❌ Something went wrong. Please try again with a different question."