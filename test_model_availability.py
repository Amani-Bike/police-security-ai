import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Try to test model availability without hanging
api_key = os.getenv("GEMINI_API_KEY")

def test_model_availability():
    # List of models to test with a very short timeout and limited retries
    models_to_try = [
        "gemini-1.0-pro",  # Most likely to be available 
        "gemini-pro",      # Standard model
        "gemini-1.5-pro",  # More advanced, may have availability limits
        "gemini-1.5-flash" # Latest, may have availability limits
    ]

    for model_name in models_to_try:
        print(f"Testing: {model_name}")
        try:
            # Create instance with minimal timeout
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.0,
                request_timeout=5  # 5 second timeout
            )
            
            # Try to make a simple call with a short timeout
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Request timed out")

            # Set up timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)  # 10 second alarm
            
            try:
                response = llm.invoke("test")
                signal.alarm(0)  # Cancel alarm
                print(f"SUCCESS: {model_name} is available")
                return llm  # Return the working model
            except TimeoutError:
                print(f"TIMEOUT: {model_name} took too long")
                signal.alarm(0)  # Cancel alarm
                continue
            except Exception as e:
                signal.alarm(0)  # Cancel alarm
                print(f"ERROR: {model_name} failed - {str(e)[:100]}")
                continue
        except Exception as e:
            print(f"INIT ERROR: {model_name} - {str(e)[:100]}")
            continue
    
    print("No models could be initialized")
    return None

if __name__ == "__main__":
    test_model_availability()