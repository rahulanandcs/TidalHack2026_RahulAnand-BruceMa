#!/usr/bin/env python3
"""
ONE-COMMAND FIX for NLTK data issue
Just run: python fix_nltk.py
"""

import nltk

print("Downloading NLTK data...")
print("This is a one-time setup and will take about 30 seconds...")
print()

# Download all required NLTK data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

print()
print("=" * 60)
print("✓ Done! NLTK data installed successfully.")
print("=" * 60)
print()
print("Now you can run:")
print("  python resume_parser_final.py your_resume.pdf")
print()
