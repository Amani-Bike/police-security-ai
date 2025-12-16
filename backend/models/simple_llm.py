import os
from typing import List
from pathlib import Path

# Try to import LangChain with Google Gemini support
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_GEMINI_AVAILABLE = True
except ImportError:
    print("Warning: langchain-google-genai not installed. Install with: pip install langchain-google-genai")
    LANGCHAIN_GEMINI_AVAILABLE = False

class SimpleLLMService:
    def __init__(self, use_gemini: bool = True):
        """
        Simple LLM service using Google Gemini
        """
        self.llm = None
        self.chat_chain = None
        self.emergency_chain = None

        if use_gemini and LANGCHAIN_GEMINI_AVAILABLE:
            self._setup_gemini()
        else:
            print("Success: Using simple response system")

    def _setup_gemini(self):
        """Setup Google Gemini using LangChain"""
        try:
            # Get API key from environment
            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                print("Warning: GEMINI_API_KEY environment variable not set.")
                print("To use Gemini, set GEMINI_API_KEY in your .env file.")
                return

            print("Setting up Google Gemini via LangChain...")

            # Initialize LLM with the most likely available model first
            # Try gemini models in order of preference, starting with most commonly available
            # Updated to include newest models (note: availability may vary by region/api key)
            available_models = [
                "gemini-2.5-flash",  # Newest model, if available with your API key
                "gemini-1.5-pro",    # More advanced, may have restrictions
                "gemini-1.5-flash",  # Latest widely available
                "gemini-pro",        # Standard model, good availability
                "gemini-1.0-pro"     # Original, most likely to be available
            ]

            for model_name in available_models:
                try:
                    print(f"Trying to initialize model: {model_name}")
                    # Initialize with specific configuration to avoid retry loops
                    # Note: ChatGoogleGenerativeAI uses google genai parameters
                    self.llm = ChatGoogleGenerativeAI(
                        model=model_name,
                        google_api_key=api_key,
                        temperature=0.7,
                        max_output_tokens=1000,  # Increase token limit for longer responses
                        # Using available parameters for timeout
                        request_timeout=5  # Timeout for individual requests in seconds
                    )
                    # For now, just try to initialize without actually testing call
                    # because of the infinite retry behavior in the Google API
                    print(f"Initialized {model_name}, skipping live test to avoid retry loops")
                    break  # Assume initialization worked and continue
                except Exception as e:
                    print(f"Model {model_name} not available: {e}")
                    self.llm = None  # Reset in case it was set but failed validation
                    continue  # Try next model

            if self.llm is None:
                print("No Gemini models available, falling back to simple responses")
                return

            print("Success: Google Gemini initialized via LangChain")

            # Load prompts from templates
            self._setup_chains()

        except Exception as e:
            print(f"Error setting up Gemini: {e}")
            print("Warning: Falling back to simple responses")
            self.llm = None

    def _load_template(self, template_name: str) -> str:
        """Load prompt template from file"""
        try:
            template_path = Path(__file__).parent.parent / "templates" / f"{template_name}.txt"
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except:
            pass

        # Default templates if files not found
        if template_name == "chat_prompt":
            return """You are Malawi Security Assistant. Answer based on this context: {context}

User query: {query}

Response:"""
        elif template_name == "emergency_prompt":
            return """EMERGENCY - {emergency_type}

User report: {query}

Context: {context}

Emergency response:"""

        return "Question: {query}\n\nAnswer:"

    def _setup_chains(self):
        """Setup LangChain chains for Gemini"""
        try:
            # Load chat prompt template
            chat_template_str = self._load_template("chat_prompt")
            chat_prompt = PromptTemplate.from_template(chat_template_str)
            self.chat_chain = chat_prompt | self.llm | StrOutputParser()

            # Load emergency prompt template
            emergency_template_str = self._load_template("emergency_prompt")
            emergency_prompt = PromptTemplate.from_template(emergency_template_str)
            self.emergency_chain = emergency_prompt | self.llm | StrOutputParser()

            # Test one of the chains with a simple query to verify it works without retries
            # This will help us detect if the model is truly available
            try:
                test_response = self.chat_chain.invoke({
                    "context": "test",
                    "query": "hello"
                })
                print("Success: LangChain chains created and tested")
            except Exception as test_error:
                error_str = str(test_error)
                # Check if this is an error that indicates model issues
                if ("NotFound" in error_str or "404" in error_str or
                    "not found" in error_str.lower() or "not supported" in error_str.lower()):
                    print(f"Model test failed: {test_error}")
                    print("Disabling LLM due to model availability issues")
                    self.llm = None  # Disable LLM to prevent retry loops
                    self.chat_chain = None
                    self.emergency_chain = None
                    return  # Exit immediately since model isn't truly available
                else:
                    print(f"Chain test had other error: {test_error}")
                    # Still continue with chains since it might be a one-time issue

        except Exception as e:
            print(f"Error setting up chains: {e}")
            # Disable the LLM to prevent issues in generate_response
            self.llm = None

    def generate_response(self, query: str, context_docs: List[str],
                          is_emergency: bool = False, emergency_type: str = None) -> str:
        """
        Generate response using Google Gemini
        """

        # Format context
        context = self._format_context(context_docs)

        # Use LLM chain if available
        if self.llm is not None:
            # Check specifically for common errors that indicate model issues
            try:
                if is_emergency and emergency_type and self.emergency_chain:
                    # Use emergency chain
                    response = self.emergency_chain.invoke({
                        "emergency_type": emergency_type,
                        "query": query,
                        "context": context
                    })
                elif self.chat_chain:
                    # Use chat chain
                    response = self.chat_chain.invoke({
                        "context": context,
                        "query": query
                    })
                else:
                    # Fallback if chains not properly set up
                    # Create a basic prompt template to use if chains aren't properly configured
                    from langchain_core.prompts import PromptTemplate
                    from langchain_core.output_parsers import StrOutputParser

                    basic_template = PromptTemplate.from_template(
                        "You are Malawi Security Assistant. Answer the user's query based on the provided context.\n\n"
                        "Context: {context}\n\n"
                        "User Query: {query}\n\n"
                        "Provide a detailed and complete response:"
                    )
                    basic_chain = basic_template | self.llm | StrOutputParser()
                    response = basic_chain.invoke({
                        "context": context,
                        "query": query
                    })

                return response.strip()

            except Exception as e:
                error_str = str(e)
                # Check if this is a model availability or access error that causes retries
                if ("NotFound" in error_str or "404" in error_str or
                    "not found" in error_str.lower() or "not supported" in error_str.lower() or
                    "ResourceExhausted" in error_str or "quota exceeded" in error_str.lower() or
                    "per minute" in error_str.lower() or "per day" in error_str.lower()):
                    print(f"Model access error detected: {e}")
                    print("Switching to simple responses to avoid retry loops")
                    # Set llm to None to prevent future attempts with broken model
                    self.llm = None
                    # Fall through to simple response
                else:
                    print(f"Warning: Gemini chain error: {e}")
                    print(f"Error type: {type(e).__name__}")

        # Simple fallback responses
        return self._simple_fallback(query, context, is_emergency, emergency_type)

    def _format_context(self, context_docs: List[str]) -> str:
        """Simple context formatting"""
        if not context_docs:
            return "No specific context available."

        # Just join the top 2 documents
        return "\n\n".join([doc[:300] for doc in context_docs[:2]])

    def _simple_fallback(self, query: str, context: str,
                         is_emergency: bool, emergency_type: str) -> str:
        """Simple fallback when LLM is not available"""

        if is_emergency:
            emergency_responses = {
                'medical': "MEDICAL EMERGENCY! Call 999 immediately. Describe symptoms and location. Do not move injured persons.",
                'crime': "CRIME EMERGENCY! Call 997 immediately. Move to safe location if possible. Note suspect details.",
                'fire': "FIRE EMERGENCY! Call 998 immediately. Evacuate building. Do not re-enter.",
                'domestic': "DOMESTIC VIOLENCE! Call 997 immediately. Seek safe location. Contact trusted person."
            }
            return emergency_responses.get(emergency_type, "EMERGENCY! Call 997 or use emergency button.")

        # Simple responses for common questions
        query_lower = query.lower()

        if any(word in query_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm Malawi Security Assistant. How can I help with security information?"

        if 'your name' in query_lower:
            return "I'm Malawi Security Assistant, your AI helper for security and emergency information in Malawi."

        if 'right' in query_lower and 'police' in query_lower:
            return """Your rights when stopped by police in Malawi:
1. Right to know why you're stopped
2. Right to remain silent
3. Right to a lawyer
4. Right to be treated with respect
Police: 997, Complaints: 0999 127 127"""

        if 'domestic' in query_lower or 'violence' in query_lower:
            return """Domestic violence support in Malawi:
• Call 997 for immediate help
• Contact social welfare services
• Safe shelters available
• Legal aid: 01 774 488"""

        if 'emergency' in query_lower and 'number' in query_lower:
            return """Malawi emergency numbers:
• Police: 997
• Fire: 998
• Medical: 999
• Child Protection: 116"""

        if 'medical' in query_lower and 'emergency' in query_lower:
            return """Medical emergency in Malawi:
1. Call 999 immediately
2. Describe symptoms
3. Provide location
4. Do not move seriously injured persons"""

        # Use context if available
        if context:
            return f"Based on Malawi security information: {context[:200]}..."

        return "I can help with security, emergencies, and safety information for Malawi. What do you need?"

# Global instance
simple_llm_service = SimpleLLMService(use_gemini=True)