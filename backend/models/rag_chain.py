import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
from typing import List, Tuple

# Import the simple LLM service
from .simple_llm import simple_llm_service

class RAGSecurityAssistant:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.knowledge_base_path = os.path.join(self.project_root, "knowledge_base")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.documents = []
        self._setup_rag()

    def _setup_rag(self):
        """Simple RAG setup"""
        print("Setting up RAG...")

        # Load or create index
        try:
            index_path = os.path.join(self.knowledge_base_path, "faiss_index.index")
            docs_path = os.path.join(self.knowledge_base_path, "documents.pkl")

            if os.path.exists(index_path) and os.path.exists(docs_path):
                self.index = faiss.read_index(index_path)
                with open(docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                print(f"Success: Loaded {len(self.documents)} documents")
            else:
                self._create_index()
        except:
            self._create_empty_index()

    def _create_empty_index(self):
        """Create empty index"""
        self.index = faiss.IndexFlatL2(384)
        self.documents = []
        print("Success: Created empty index")

    def _create_index(self):
        """Create index from documents"""
        try:
            # Load all text files
            all_docs = []
            for file in os.listdir(self.knowledge_base_path):
                if file.endswith('.txt'):
                    with open(os.path.join(self.knowledge_base_path, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Split into paragraphs
                    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                    all_docs.extend(paragraphs[:10])  # Limit per file

            if all_docs:
                self.documents = all_docs
                embeddings = self.model.encode(all_docs)
                self.index = faiss.IndexFlatL2(embeddings.shape[1])
                self.index.add(embeddings.astype('float32'))

                # Save
                faiss.write_index(self.index, os.path.join(self.knowledge_base_path, "faiss_index.index"))
                with open(os.path.join(self.knowledge_base_path, "documents.pkl"), 'wb') as f:
                    pickle.dump(self.documents, f)

                print(f"Success: Created index with {len(self.documents)} documents")
            else:
                self._create_empty_index()
        except:
            self._create_empty_index()

    def search(self, query: str, k: int = 3) -> List[str]:
        """Enhanced search with better relevance scoring"""
        if not self.documents:
            return []

        try:
            import re

            # Get the top results from semantic search
            query_embedding = self.model.encode([query])
            _, indices = self.index.search(query_embedding.astype('float32'), k * 2)  # Get more candidates

            # Rerank results based on keyword matching and relevance
            candidate_docs = []
            for i in indices[0]:
                if i < len(self.documents):
                    doc = self.documents[i]
                    candidate_docs.append((doc, i))

            # Calculate relevance score based on keyword matching
            query_words = set(re.findall(r'\w+', query.lower()))

            scored_docs = []
            for doc, idx in candidate_docs:
                doc_lower = doc.lower()
                doc_words = set(re.findall(r'\w+', doc_lower))

                # Calculate intersection of query words and document words
                intersection = query_words.intersection(doc_words)
                keyword_score = len(intersection) / len(query_words) if query_words and len(query_words) > 0 else 0

                # Length-based scoring (too long documents may not be appropriate)
                length_score = min(len(doc), 500) / 500

                # Overall score
                overall_score = keyword_score * 0.7 + length_score * 0.3
                scored_docs.append((doc, overall_score))

            # Sort by score and return top k
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return [doc for doc, score in scored_docs[:k] if score > 0]
        except Exception as e:
            print(f"Search error: {e}")
            # Fallback to original method
            try:
                query_embedding = self.model.encode([query])
                _, indices = self.index.search(query_embedding.astype('float32'), k)
                return [self.documents[i] for i in indices[0] if i < len(self.documents)]
            except:
                return []

    def get_knowledge_base_stats(self):
        """Return statistics about the knowledge base"""
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal if self.index else 0,
            "model_type": "SentenceTransformer all-MiniLM-L6-v2"
        }

    def _detect_emergency(self, query: str):
        """Improved emergency detection with more context awareness"""
        query_lower = query.lower().strip()

        # More specific emergency indicators - avoid false positives
        # Don't flag general questions like "what can you help me", "how", "what", etc.
        emergency_keywords = [
            # Medical emergencies
            'bleeding', 'heart attack', 'heartattack', 'unconscious', 'fainted', 'faint',
            'difficulty breathing', 'can\'t breathe', 'breathing problems', 'seizure',
            'sick', 'medicine', 'pain', 'hurt', 'injury', 'injured', 'accident', 'hit by',

            # Crime emergencies
            'attacking', 'being attacked', 'attack', 'robbery', 'robbing', 'robbed',
            'crime in', 'crime happening', 'burglary', 'burglar', 'break in', 'breaking in',
            'stolen', 'being robbed', 'assault', 'assaulted', 'kidnapped', 'kidnapping',
            'murder', 'murdered', 'killed', 'killing', 'shooting', 'shot',

            # Fire emergencies
            'fire', 'burning', 'smoke', 'house fire', 'building fire', 'on fire',
            'burned down', 'burning down',

            # Accident emergencies
            'car accident', 'crash', 'hit by car', 'car hit', 'vehicle accident',

            # Urgent help needed
            'emergency', 'urgent help', 'immediately', 'right now', 'save me', 'help me now',
            'need help now', 'danger', 'in danger', 'please help'
        ]

        # Words that indicate it's NOT an emergency (to avoid false positives)
        non_emergency_indicators = [
            'what can you', 'how can', 'what is', 'what are', 'tell me', 'explain',
            'no it is not', 'not emergency', 'not urgent', 'just asking', 'i wonder',
            'can you tell', 'i want to know', 'question', 'info about', 'information about'
        ]

        # Check if this is explicitly NOT an emergency
        is_definitely_not_emergency = any(indicator in query_lower for indicator in non_emergency_indicators)

        if is_definitely_not_emergency:
            return False, None

        # Check for emergency indicators
        has_emergency = any(indicator in query_lower for indicator in emergency_keywords)

        if has_emergency:
            # Determine specific type with better context
            if any(word in query_lower for word in ['heart', 'bleeding', 'unconscious', 'fainted',
                                                   'difficulty breathing', 'can\'t breathe', 'seizure',
                                                   'sick', 'medicine', 'pain', 'hurt', 'injury', 'injured']):
                return True, 'medical'
            elif any(word in query_lower for word in ['rob', 'stolen', 'crime', 'murder',
                                                     'burglar', 'burglary', 'theft', 'kill', 'assault',
                                                     'attack', 'shooting', 'kidnap']):
                return True, 'crime'
            elif any(word in query_lower for word in ['fire', 'burning', 'smoke', 'on fire']):
                return True, 'fire'
            elif any(word in query_lower for word in ['abuse', 'domestic', 'violence', 'hit me',
                                                     'hitting', 'assaulted', 'assault']):
                return True, 'domestic'
            else:
                # General emergency if specific type not detected
                return True, 'general'

        return False, None

    def generate_response(self, query: str, chat_history: List[Tuple[str, str]] = None) -> dict:
        """Improved response generation with better error handling"""
        try:
            # 1. Search for context
            context_docs = self.search(query)

            # 2. Detect emergency
            is_emergency, emergency_type = self._detect_emergency(query)

            # 3. Generate response with simple LLM service
            response = simple_llm_service.generate_response(
                query=query,
                context_docs=context_docs,
                is_emergency=is_emergency,
                emergency_type=emergency_type
            )

            # Ensure response is properly formatted
            if isinstance(response, str):
                return {
                    "reply": response,
                    "is_emergency": is_emergency,
                    "emergency_type": emergency_type
                }
            elif isinstance(response, dict):
                return response
            else:
                return {
                    "reply": "I can help with security, emergencies, and safety information for Malawi. What do you need?",
                    "is_emergency": False,
                    "emergency_type": None
                }

        except Exception as e:
            print(f"Error in generate_response: {e}")
            # Use a simple direct fallback since we can't call simple_fallback with proper params in error context
            return {
                "reply": "I can help with security, emergencies, and safety information for Malawi. What do you need?",
                "is_emergency": False,
                "emergency_type": None
            }

# Global instance
security_assistant = RAGSecurityAssistant()