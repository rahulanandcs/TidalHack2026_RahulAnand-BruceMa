from flask import Flask, request, jsonify, send_from_directory
import os
from google import genai

app = Flask(__name__, static_folder='.')

# Manual CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Initialize Gemini client with the new API
client = genai.Client(api_key="AIzaSyCSIqtgnFftPSlrVSA8iWswlueyLZyY1cs")

@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'winter_penguin_page.html')

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_career():
    """API endpoint to process career analysis request"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Read the files
        with open("resume_information.txt", "r", encoding='utf-8') as f:
            resume = f.read()
        
        with open("company_information.txt", "r", encoding='utf-8') as f:
            companies = f.read()
        
        with open("response_format.txt", "r", encoding='utf-8') as f:
            format_text = f.read()
        
        # Build the question
        question = (format_text + "\n\n\nThis is my resume: \n" + resume + 
                   "\n\n\n" + "These are the company information: \n" + companies)
        
        # Call Gemini API using the new google-genai package
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=question
        )
        
        return jsonify({
            'success': True,
            'result': response.text
        })
        
    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': f'File not found: {str(e)}. Make sure resume_information.txt, company_information.txt, and response_format.txt are in the same folder as this script.'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, images)"""
    return send_from_directory('.', path)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Career Compass Backend Server")
    print("="*50)
    print(f"Server running at: http://localhost:5000")
    print(f"API endpoint: http://localhost:5000/api/analyze")
    print("Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)