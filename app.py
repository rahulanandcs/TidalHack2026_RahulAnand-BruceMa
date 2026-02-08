"""
Career Compass Flask Backend - LOCAL ONLY
Handles: Resume Upload -> Parse -> Company Scraping -> Gemini Analysis -> Return to Chatbot
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
from pathlib import Path

# Import your parsers
from resume_parser_final import FinalResumeParser
from career_fair_scraper import CareerFairScraper

# Import Gemini
from google import genai

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for local development

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialize Gemini
GEMINI_API_KEY = "AIzaSyD8_gbsuBcOWQvILCYMApC5bP96-eqKnVw"
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Store parsed data in memory (resets when server restarts)
current_session = {
    'resume_json': None,
    'companies_json': None,
    'analysis_result': None
}


@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')


@app.route('/upload', methods=['POST'])
def upload_resume():
    """
    Handle resume upload from index.html
    Returns: Parsed resume JSON
    """
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files allowed'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"✓ File saved: {filepath}")
        
        # Parse the resume
        parser = FinalResumeParser()
        resume_json = parser.parse_to_dict(filepath)
        
        print(f"✓ Resume parsed: {resume_json['contact']['name']}")
        
        # Store in session
        current_session['resume_json'] = resume_json
        
        # Save to JSON file for Gemini to read
        with open('resume_information.json', 'w') as f:
            json.dump(resume_json, f, indent=2)
        
        # Also create a text version for Gemini
        resume_text = format_resume_for_gemini(resume_json)
        with open('resume_information.txt', 'w') as f:
            f.write(resume_text)
        
        print("✓ Resume saved to files")
        
        # Clean up uploaded PDF
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Resume uploaded and parsed successfully',
            'resume_data': resume_json
        }), 200
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/scrape-companies', methods=['POST'])
def scrape_companies():
    """
    Scrape company data from career fair URL
    Expected JSON: { "url": "https://..." }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'Missing URL in request'}), 400
        
        url = data['url']
        print(f"Scraping URL: {url}")
        
        # Scrape the company data
        scraper = CareerFairScraper(headless=True)
        try:
            company_data = scraper.scrape_employer_page(url)
            
            # Store in session
            current_session['companies_json'] = company_data
            
            # Save to JSON file
            with open('company_information.json', 'w') as f:
                json.dump(company_data, f, indent=2)
            
            # Create text version for Gemini
            company_text = format_company_for_gemini(company_data)
            with open('company_information.txt', 'w') as f:
                f.write(company_text)
            
            print(f"✓ Company data scraped: {company_data.get('company_name', 'Unknown')}")
            
            return jsonify({
                'success': True,
                'message': 'Company data scraped successfully',
                'company_data': company_data
            }), 200
            
        finally:
            scraper.close()
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_career():
    """
    Run Gemini analysis using resume + company data
    Called from chatbot.html
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        print("\n" + "="*50)
        print("Starting Gemini Analysis...")
        print("="*50)
        
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
        
        print("✓ Files read successfully")
        print(f"✓ Question length: {len(question)} characters")
        
        # Call Gemini API
        print("✓ Calling Gemini API...")
        # Try multiple model names in order of preference
        models_to_try = [
            'gemini-2.5-flash',
            'models/gemini-2.5-pro',
            'models/gemini-2.0-flash'
        ]
        
        response = None
        last_error = None
        
        for model_name in models_to_try:
            try:
                print(f"  Trying model: {model_name}")
                response = gemini_client.models.generate_content(
                    model=model_name,
                    contents=question
                )
                print(f"  ✓ Success with {model_name}")
                break
            except Exception as e:
                print(f"  ✗ {model_name} failed: {str(e)[:100]}")
                last_error = e
                continue
        
        if response is None:
            raise Exception(f"All models failed. Last error: {str(last_error)}")
        
        result = response.text
        print(f"✓ Got response: {len(result)} characters")
        
        # Store in session
        current_session['analysis_result'] = result
        
        return jsonify({
            'success': True,
            'result': result,
            'resume_name': current_session.get('resume_json', {}).get('contact', {}).get('name'),
            'company_name': current_session.get('companies_json', {}).get('company_name')
        })
    
    except FileNotFoundError as e:
        print(f"✗ File not found: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'File not found: {str(e)}. Make sure resume_information.txt and company_information.txt exist.'
        }), 404
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@app.route('/get-session-data', methods=['GET'])
def get_session_data():
    """Get current session data (for chatbot to check if resume is uploaded)"""
    return jsonify({
        'has_resume': current_session['resume_json'] is not None,
        'has_companies': current_session['companies_json'] is not None,
        'resume_name': current_session.get('resume_json', {}).get('contact', {}).get('name') if current_session['resume_json'] else None,
        'company_name': current_session.get('companies_json', {}).get('company_name') if current_session['companies_json'] else None
    })


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)


def format_resume_for_gemini(resume_json):
    """Convert resume JSON to formatted text for Gemini"""
    text = "RESUME INFORMATION\n"
    text += "="*50 + "\n\n"
    
    # Contact Info
    contact = resume_json.get('contact', {})
    text += f"Name: {contact.get('name', 'N/A')}\n"
    text += f"Email: {contact.get('email', 'N/A')}\n"
    text += f"Phone: {contact.get('phone', 'N/A')}\n"
    text += f"Location: {contact.get('location', 'N/A')}\n"
    if contact.get('linkedin'):
        text += f"LinkedIn: {contact.get('linkedin')}\n"
    if contact.get('github'):
        text += f"GitHub: {contact.get('github')}\n"
    text += "\n"
    
    # Skills
    skills = resume_json.get('skills', [])
    if skills:
        text += "SKILLS:\n"
        text += ", ".join(skills) + "\n\n"
    
    # Education
    education = resume_json.get('education', [])
    if education:
        text += "EDUCATION:\n"
        for edu in education:
            text += f"- {edu.get('degree', 'N/A')}\n"
            text += f"  {edu.get('institution', 'N/A')}\n"
            if edu.get('year'):
                text += f"  {edu.get('year')}\n"
            text += "\n"
    
    # Experience
    experience = resume_json.get('experience', [])
    if experience:
        text += "EXPERIENCE:\n"
        for exp in experience:
            text += f"- {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}\n"
            if exp.get('duration'):
                text += f"  {exp.get('duration')}\n"
            if exp.get('description'):
                for desc in exp.get('description', [])[:3]:  # First 3 bullets
                    text += f"  • {desc}\n"
            text += "\n"
    
    return text


def format_company_for_gemini(company_json):
    """Convert company JSON to formatted text for Gemini"""
    text = "COMPANY INFORMATION\n"
    text += "="*50 + "\n\n"
    
    text += f"Company Name: {company_json.get('company_name', 'N/A')}\n\n"
    
    if company_json.get('about'):
        text += f"About:\n{company_json.get('about')}\n\n"
    
    if company_json.get('we_are_looking_for'):
        text += f"We Are Looking For:\n{company_json.get('we_are_looking_for')}\n\n"
    
    if company_json.get('industry'):
        text += f"Industry: {company_json.get('industry')}\n\n"
    
    if company_json.get('website'):
        text += f"Website: {company_json.get('website')}\n\n"
    
    if company_json.get('position_types'):
        text += f"Position Types: {', '.join(company_json.get('position_types', []))}\n\n"
    
    if company_json.get('majors_recruited'):
        text += f"Majors Recruited: {', '.join(company_json.get('majors_recruited', []))}\n\n"
    
    return text


if __name__ == '__main__':
    print("\n" + "="*70)
    print("CAREER COMPASS - LOCAL SERVER")
    print("="*70)
    print("Server running at: http://localhost:5001")
    print("\nEndpoints:")
    print("  POST /upload                - Upload resume PDF")
    print("  POST /scrape-companies      - Scrape company data")
    print("  POST /api/analyze           - Run Gemini analysis")
    print("  GET  /get-session-data      - Check current session")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")
    
    app.run(debug=True, port=5001, host='0.0.0.0')