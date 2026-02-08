"""
Test Gemini API Connection and List Available Models
Run this to find the correct model name for your API key
"""

from google import genai

# Your API key
API_KEY = "AIzaSyC4TWd8GiAItBBdljmkQnYdKcVbK9dseZ0"

print("="*70)
print("GEMINI API TEST")
print("="*70)

try:
    # Initialize client
    client = genai.Client(api_key=API_KEY)
    print("✓ Client initialized successfully\n")
    
    # Try to list available models
    print("Attempting to list available models...")
    try:
        models = client.models.list()
        print("\n✓ Available models:")
        print("-"*70)
        for model in models:
            print(f"  • {model.name}")
        print("-"*70)
    except Exception as e:
        print(f"✗ Could not list models: {e}\n")
    
    # Test common model names
    print("\nTesting common model names:")
    print("-"*70)
    
    test_models = [
        'gemini-1.5-flash',
        'gemini-1.5-pro', 
        'gemini-pro',
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro-latest',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro',
        'models/gemini-pro'
    ]
    
    test_prompt = "Say 'Hello' in one word."
    
    for model_name in test_models:
        try:
            print(f"\nTrying: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=test_prompt
            )
            print(f"  ✓ SUCCESS!")
            print(f"  Response: {response.text[:50]}")
            print(f"\n  *** USE THIS MODEL: {model_name} ***\n")
            break
        except Exception as e:
            error_msg = str(e)
            if '404' in error_msg:
                print(f"  ✗ Not found (404)")
            elif '403' in error_msg:
                print(f"  ✗ Permission denied (403)")
            else:
                print(f"  ✗ Error: {error_msg[:100]}")
    
except Exception as e:
    print(f"\n✗ Fatal error: {e}")
    print("\nPossible issues:")
    print("  1. Invalid API key")
    print("  2. API key doesn't have access to Gemini models")
    print("  3. Wrong google-generativeai package version")
    print("\nTry:")
    print("  pip install --upgrade google-generativeai")

print("\n" + "="*70)
