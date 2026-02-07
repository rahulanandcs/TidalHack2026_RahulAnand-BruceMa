# Resume Parser

A Python-based resume parser that extracts structured data from PDF resumes.

## Features

- 📧 **Contact Information**: Email, phone, LinkedIn, GitHub
- 🎓 **Education**: Degrees, institutions, GPA, graduation years
- 💼 **Experience**: Job titles, companies, duration, descriptions
- 🛠️ **Skills**: Technical skills and competencies
- 📄 **JSON Export**: Output structured data as JSON

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/resume-parser.git
cd resume-parser
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install PyPDF2
```

## Usage

### Command Line

Parse a single resume:
```bash
python resume_parser.py path/to/resume.pdf
```

This will:
- Display extracted information in the terminal
- Save a JSON file with the parsed data (e.g., `resume_parsed.json`)

### As a Python Module

```python
from resume_parser import ResumeParser

# Initialize parser
parser = ResumeParser()

# Parse resume to dictionary
data = parser.parse_to_dict('resume.pdf')

# Parse resume to JSON file
json_output = parser.parse_to_json('resume.pdf', 'output.json')

# Parse resume to object (for more control)
parsed_resume = parser.parse('resume.pdf')
print(parsed_resume.contact.email)
print(parsed_resume.skills)
```

## Output Format

The parser outputs JSON in this structure:

```json
{
  "contact": {
    "name": "John Doe",
    "email": "john.doe@email.com",
    "phone": "123-456-7890",
    "linkedin": "linkedin.com/in/johndoe",
    "github": "github.com/johndoe",
    "location": null
  },
  "skills": [
    "python",
    "javascript",
    "react",
    "machine learning"
  ],
  "education": [
    {
      "degree": "Bachelor of Science in Computer Science",
      "institution": "University Name",
      "year": "2020",
      "gpa": "3.8"
    }
  ],
  "experience": [
    {
      "title": "Software Engineer",
      "company": "Tech Company",
      "duration": "Jan 2020 - Present",
      "description": "Developed features..."
    }
  ]
}
```

## Customization

### Adding More Skills

Edit the `COMMON_SKILLS` set in `ResumeParser` class:

```python
COMMON_SKILLS = {
    'python', 'java', 'javascript',
    # Add your skills here
    'kotlin', 'swift', 'flutter'
}
```

### Adjusting Section Headers

Modify `SECTION_HEADERS` to match different resume formats:

```python
SECTION_HEADERS = {
    'experience': ['experience', 'work history', 'employment'],
    'education': ['education', 'academic background'],
    # Add more variations
}
```

## Batch Processing

Process multiple resumes:

```python
from pathlib import Path
from resume_parser import ResumeParser

parser = ResumeParser()
resume_dir = Path('resumes')

for pdf_file in resume_dir.glob('*.pdf'):
    try:
        data = parser.parse_to_dict(str(pdf_file))
        output_file = pdf_file.with_suffix('.json')
        parser.parse_to_json(str(pdf_file), str(output_file))
        print(f"✓ Parsed: {pdf_file.name}")
    except Exception as e:
        print(f"✗ Error parsing {pdf_file.name}: {e}")
```

## Known Limitations

- **PDF Format**: Works best with text-based PDFs. Scanned/image PDFs require OCR (not included)
- **Resume Formats**: Parser uses heuristics and may need tuning for different formats
- **Name Extraction**: Simple heuristic that may need refinement
- **Section Detection**: Relies on common header keywords

## Improvements for Your Hackathon

Consider adding:

1. **OCR Support**: Use `pytesseract` for scanned PDFs
2. **Web Interface**: Flask/FastAPI + simple HTML form
3. **Database Storage**: Store parsed resumes in SQLite/PostgreSQL
4. **Matching Algorithm**: Score resumes against job descriptions
5. **Bulk Upload**: Process multiple resumes at once
6. **Export Options**: CSV, Excel, or database export
7. **Advanced NLP**: Use spaCy for better entity recognition

## Quick Web Interface (Optional)

Want to add a web UI? Here's a minimal Flask example:

```python
from flask import Flask, request, jsonify
from resume_parser import ResumeParser

app = Flask(__name__)
parser = ResumeParser()

@app.route('/parse', methods=['POST'])
def parse_resume():
    file = request.files['resume']
    file.save('temp.pdf')
    result = parser.parse_to_dict('temp.pdf')
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

## Contributing

For your hackathon team:
1. Create feature branches: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -am "Add feature"`
3. Push and create PR: `git push origin feature/your-feature`

## License

MIT License - free to use for your hackathon!

## Troubleshooting

**PyPDF2 can't extract text?**
- PDF might be scanned/image-based - needs OCR
- Try updating PyPDF2: `pip install --upgrade PyPDF2`

**Skills not detected?**
- Add more keywords to `COMMON_SKILLS`
- Check if resume has a "Skills" section with that exact header

**Sections not found?**
- Resume might use different header names
- Add variations to `SECTION_HEADERS`
