"""
Test script to verify google-generativeai installation
"""

print("Testing google-generativeai import...")

try:
    import google.generativeai as genai
    print("✓ Successfully imported google.generativeai as genai")
    print(f"✓ Version: {genai.__version__ if hasattr(genai, '__version__') else 'unknown'}")
except ImportError as e:
    print(f"✗ Failed to import google.generativeai")
    print(f"Error: {e}")
    
try:
    import google
    print(f"✓ Google package found at: {google.__file__}")
except ImportError:
    print("✗ Google package not found")

print("\n--- Checking alternative imports ---")

try:
    from google import generativeai
    print("✓ Alternative import works: from google import generativeai")
except ImportError as e:
    print(f"✗ Alternative import failed: {e}")

print("\n--- System Information ---")
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
