# Career Compass - Backend Integration Guide

## Overview
This integration connects your Flask backend with the Career Compass frontend using a REST API.

## Architecture
- **Backend**: Flask server with Google Gemini API integration
- **Frontend**: HTML/CSS/JavaScript winter penguin theme
- **Communication**: REST API with JSON responses

## Setup Instructions

### 1. Install Dependencies

```bash
pip install flask flask-cors google-genai
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

### 2. File Structure

Make sure your project has this structure:

```
project_folder/
├── app.py                          # Flask backend
├── winter_penguin_page.html        # Frontend HTML
├── requirements.txt                # Python dependencies
├── resume_information.txt          # Your resume data
├── company_information.txt         # Company data
├── response_format.txt             # Format instructions for Gemini
├── style.css                       # (if you have external CSS)
├── navbar.css                      # (if you have external CSS)
└── images/                         # Image assets folder
    ├── careerCompassLogo.png
    ├── miniCCLogo.png
    └── bwProfile.png
```

### 3. Update File Paths

The Flask backend (`app.py`) expects these files in the same directory:
- `resume_information.txt`
- `company_information.txt`
- `response_format.txt`

If your files are in a different location, update the paths in `app.py`.

### 4. Run the Application

#### Start the Flask server:

```bash
python app.py
```

The server will start on `http://localhost:5000`

#### Open the frontend:

Navigate to `http://localhost:5000` in your web browser.

### 5. How It Works

1. **User clicks the button** "Bridge the Gap. Own the Conversation."
2. **JavaScript sends a POST request** to `/api/analyze`
3. **Flask backend**:
   - Reads the resume, company info, and format files
   - Sends the data to Google Gemini API
   - Returns the AI-generated response
4. **Frontend displays the result** in a styled container below the button

## API Endpoint

### POST `/api/analyze`

**Response Success:**
```json
{
  "success": true,
  "result": "AI-generated career analysis..."
}
```

**Response Error:**
```json
{
  "success": false,
  "error": "Error message"
}
```

## Important Notes

### Security Considerations

⚠️ **Your API key is exposed in the code!** For production:

1. **Use environment variables:**

```python
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
```

2. **Create a `.env` file:**

```
GEMINI_API_KEY=AIzaSyCWpGU-Ld_XWThx5VzWuo08_GPFPvYyQbU
```

3. **Add `.env` to `.gitignore`**

### CORS (Cross-Origin Resource Sharing)

The `flask-cors` package is included to allow the frontend to communicate with the backend. This is already configured in `app.py`.

### Gemini Model

The code now uses `gemini-2.0-flash-exp` instead of `gemini-3-flash-preview` (which doesn't exist). Update if needed:

```python
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",  # or "gemini-1.5-pro", etc.
    contents=question
)
```

## Troubleshooting

### "Unable to connect to the server"
- Make sure Flask is running (`python app.py`)
- Check that you're accessing `http://localhost:5000`

### "File not found" error
- Verify that `resume_information.txt`, `company_information.txt`, and `response_format.txt` exist in the same directory as `app.py`

### CORS errors
- Make sure `flask-cors` is installed
- The `CORS(app)` line should be in `app.py`

### API key errors
- Verify your Gemini API key is valid
- Check your API quota hasn't been exceeded

## Deployment Options

For production deployment, consider:

1. **Heroku**: Easy deployment with free tier
2. **Google Cloud Run**: Serverless container deployment
3. **AWS Elastic Beanstalk**: Scalable Flask hosting
4. **DigitalOcean App Platform**: Simple deployment

Remember to:
- Use environment variables for the API key
- Set `debug=False` in production
- Use a production WSGI server (gunicorn, uwsgi)

## Next Steps

1. Add loading animations
2. Implement error handling
3. Add user authentication
4. Store results in a database
5. Add file upload functionality for resumes
6. Implement rate limiting
7. Add result caching

## License

[Your License Here]
