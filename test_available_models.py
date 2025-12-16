from langchain_google_genai import ChatGoogleGenerativeAI
import os

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not set in environment")
    exit(1)

try:
    # Attempt to list models - unfortunately there's no direct way in langchain
    # So let's try each model individually
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-1.5-pro-latest", 
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-pro-vision",
        "gemini-1.0-pro"
    ]
    
    available_models = []
    
    for model_name in models_to_try:
        print(f"\nTrying model: {model_name}")
        try:
            llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=0.0)
            # Try a minimal request
            response = llm.invoke("Say hi")
            print(f"✓ SUCCESS: {model_name} is available")
            available_models.append(model_name)
            break  # Stop at first successful model
        except Exception as e:
            print(f"✗ FAILED: {model_name} - {str(e)[:100]}...")  # Truncate error msg
    
    if available_models:
        print(f"\nFirst available model: {available_models[0]}")
    else:
        print("\nNo models are available with your API key")
        
except Exception as e:
    print(f"Error during testing: {e}")