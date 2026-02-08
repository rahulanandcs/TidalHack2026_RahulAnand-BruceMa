"""
Resume Parser - FINAL VERSION
Uses pyresparser library with custom enhancements for better accuracy
"""

import re
from pathlib import Path
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Try to import pyresparser, fall back to PyPDF2 if not available
try:
    # First ensure NLTK data is available
    import nltk
    try:
        from nltk.corpus import stopwords
        _ = stopwords.words('english')
    except LookupError:
        print("Downloading required NLTK data (one-time setup)...")
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('maxent_ne_chunker', quiet=True)
        nltk.download('words', quiet=True)
        print("✓ NLTK data downloaded!")
    
    from pyresparser import ResumeParser as PyResumeParser
    PYRESPARSER_AVAILABLE = True
except ImportError as e:
    PYRESPARSER_AVAILABLE = False
    import PyPDF2
    if 'pyresparser' in str(e):
        print("Note: pyresparser not installed. Using basic parser.")
        print("For better results, run: pip install pyresparser")

# Try to import pdfminer for better text extraction
try:
    from pdfminer3.layout import LAParams
    from pdfminer3.pdfpage import PDFPage
    from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer3.converter import TextConverter
    import io
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False


@dataclass
class ContactInfo:
    """Contact information extracted from resume"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    location: Optional[str] = None


@dataclass
class Education:
    """Education entry"""
    degree: str
    institution: str
    year: Optional[str] = None
    gpa: Optional[str] = None
    additional_info: Optional[str] = None


@dataclass
class Experience:
    """Work experience entry"""
    title: str
    company: str
    duration: Optional[str] = None
    description: Optional[List[str]] = None


@dataclass
class ParsedResume:
    """Complete parsed resume data"""
    contact: ContactInfo
    skills: List[str]
    education: List[Education]
    experience: List[Experience]
    raw_text: str
    total_pages: int = 1


class FinalResumeParser:
    """
    Final resume parser combining pyresparser and custom parsing logic
    """
    
    def __init__(self):
        """Initialize the parser"""
        self.use_pyresparser = PYRESPARSER_AVAILABLE
        self.use_pdfminer = PDFMINER_AVAILABLE
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file using best available method
        Priority: pdfminer3 > PyPDF2
        """
        text = ""
        
        # Try pdfminer3 first (best quality)
        if self.use_pdfminer:
            try:
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
                page_interpreter = PDFPageInterpreter(resource_manager, converter)
                
                with open(pdf_path, 'rb') as fh:
                    for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                        page_interpreter.process_page(page)
                    text = fake_file_handle.getvalue()
                
                converter.close()
                fake_file_handle.close()
                return text
            except Exception as e:
                print(f"pdfminer3 failed: {e}, falling back to PyPDF2")
        
        # Fallback to PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return text
    
    def count_pdf_pages(self, pdf_path: str) -> int:
        """Count number of pages in PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except:
            return 1
    
    def find_section_bounds(self, text: str, section_keywords: List[str]) -> tuple:
        """
        Find the start and end indices of a section
        """
        lines = text.split('\n')
        
        if isinstance(section_keywords, str):
            section_keywords = [section_keywords]
        
        # Find section start
        start_idx = None
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            line_upper = line_stripped.upper()
            
            for keyword in section_keywords:
                keyword_upper = keyword.upper()
                # Match if line contains keyword and is short (likely a header)
                if keyword_upper in line_upper and len(line_stripped) < 50:
                    # Check if it's mostly just the keyword (not buried in text)
                    if line_upper == keyword_upper or line_stripped.startswith(keyword) or line_stripped.endswith(keyword):
                        start_idx = i + 1
                        break
            if start_idx is not None:
                break
        
        if start_idx is None:
            return None, None
        
        # Find section end
        end_idx = len(lines)
        all_section_keywords = ['EDUCATION', 'EXPERIENCE', 'SKILLS', 'TECHNICAL SKILLS', 
                                'ACTIVITIES', 'PROJECTS', 'AWARDS', 'SUMMARY', 'CERTIFICATIONS',
                                'PUBLICATIONS', 'HONORS', 'REFERENCES', 'OBJECTIVE']
        
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            if line and len(line) < 50:
                line_upper = line.upper()
                for keyword in all_section_keywords:
                    if keyword in line_upper and (line_upper == keyword or len(line_upper) < 30):
                        end_idx = i
                        break
                if end_idx != len(lines):
                    break
        
        return start_idx, end_idx
    
    def extract_education_custom(self, text: str) -> List[Education]:
        """Custom education extraction"""
        education_list = []
        lines = text.split('\n')
        start_idx, end_idx = self.find_section_bounds(text, ['EDUCATION', 'ACADEMIC BACKGROUND'])
        
        if start_idx is None:
            return education_list
        
        section_lines = [lines[i].strip() for i in range(start_idx, end_idx) if lines[i].strip()]
        
        i = 0
        while i < len(section_lines):
            line = section_lines[i]
            
            if not line or line.startswith('●') or line.startswith('•'):
                i += 1
                continue
            
            # First line is likely institution (with optional location)
            institution = line
            degree = ""
            year = None
            additional_info = None
            
            # Look ahead for degree and year
            if i + 1 < len(section_lines):
                next_line = section_lines[i + 1]
                
                # Check for degree indicators
                degree_indicators = ['BS:', 'BA:', 'MS:', 'MA:', 'PhD:', 'B.S.', 'M.S.', 
                                   'Bachelor', 'Master', 'Associate', 'B.E.', 'M.E.']
                
                if any(deg in next_line for deg in degree_indicators):
                    degree = next_line
                    
                    # Look for year in surrounding lines
                    for j in range(i, min(i + 5, len(section_lines))):
                        check_line = section_lines[j]
                        # Match year patterns: "Expected in May 2029", "May 2029", "2025-2029"
                        year_match = re.search(r'(?:Expected\s+in\s+)?(?:May|June|August|December|Jan|Feb|Mar|Apr|Jul|Sep|Oct|Nov)?\s*(\d{4})(?:\s*[-–]\s*(?:May|June|August|December|Jan|Feb|Mar|Apr|Jul|Sep|Oct|Nov)?\s*\d{4})?', check_line, re.IGNORECASE)
                        if year_match:
                            # Get the full match including "Expected in" if present
                            full_match = check_line[year_match.start():year_match.end()].strip()
                            # Check if "Expected" is before the match
                            before_text = check_line[:year_match.start()].lower()
                            if 'expected' in before_text:
                                year = "Expected in " + full_match
                            else:
                                year = full_match
                            break
                    
                    # Check for additional info (honors, GPA, etc.) on next line
                    if i + 2 < len(section_lines):
                        potential_additional = section_lines[i + 2]
                        # Don't include if it looks like a new institution
                        if not any(kw in potential_additional for kw in ['University', 'College', 'Institute', 'School']) and \
                           not potential_additional.startswith('BS') and not potential_additional.startswith('BA'):
                            # But do include if it mentions honors, GPA, etc
                            if any(kw in potential_additional.lower() for kw in ['honor', 'gpa', 'distinction', 'dean', 'scholarship']):
                                additional_info = potential_additional
                    
                    education_list.append(Education(
                        degree=degree,
                        institution=institution,
                        year=year,
                        additional_info=additional_info
                    ))
                    i += 3 if additional_info else 2
                else:
                    i += 1
            else:
                i += 1
        
        return education_list
    
    def extract_experience_custom(self, text: str) -> List[Experience]:
        """Custom experience extraction including ACTIVITIES and PROJECTS"""
        experience_list = []
        lines = text.split('\n')
        
        # Collect from multiple sections
        sections_to_check = [
            ['EXPERIENCE', 'WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE'],
            ['ACTIVITIES'],
            ['PROJECTS']
        ]
        
        all_section_lines = []
        
        for section_keywords in sections_to_check:
            start_idx, end_idx = self.find_section_bounds(text, section_keywords)
            if start_idx is not None:
                section_lines = [(i, lines[i].strip()) for i in range(start_idx, end_idx) if lines[i].strip()]
                all_section_lines.extend(section_lines)
        
        # Sort by line number
        all_section_lines.sort(key=lambda x: x[0])
        section_lines = [line for _, line in all_section_lines]
        
        if not section_lines:
            return experience_list
        
        # Date pattern for matching duration
        date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[-–—]\s*(Present|January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|present|\d{4})'
        
        i = 0
        while i < len(section_lines):
            line = section_lines[i]
            
            # Skip empty lines and bullet points at this level
            if not line or line.startswith('●') or line.startswith('•') or line.startswith('-'):
                i += 1
                continue
            
            # Check if this line contains a date (might be duration on its own line)
            if re.search(date_pattern, line):
                # This is likely a standalone date line, skip it
                i += 1
                continue
            
            # This should be a company/organization name
            company = line
            title = ""
            duration = None
            description = []
            
            # Look at next line for title and/or duration
            if i + 1 < len(section_lines):
                next_line = section_lines[i + 1]
                
                # Skip if next line is a bullet point (means we got company but no title)
                if next_line.startswith('●') or next_line.startswith('•') or next_line.startswith('-'):
                    # Company only, no title, collect bullets
                    i += 1
                    while i < len(section_lines) and (section_lines[i].startswith('●') or 
                                                     section_lines[i].startswith('•') or 
                                                     section_lines[i].startswith('-')):
                        bullet = section_lines[i].lstrip('●•-').strip()
                        description.append(bullet)
                        i += 1
                    
                    experience_list.append(Experience(
                        title="",
                        company=company,
                        duration=None,
                        description=description if description else None
                    ))
                    continue
                
                # Check if next line has a date pattern
                date_match = re.search(date_pattern, next_line)
                
                if date_match:
                    # Next line contains title and duration
                    duration = date_match.group(0)
                    # Everything before the date is the title
                    title = next_line[:date_match.start()].strip().strip('-–— ')
                    i += 2
                else:
                    # Next line is just the title
                    title = next_line
                    i += 2
                    
                    # Check if the line after that is a duration-only line
                    if i < len(section_lines):
                        potential_date_line = section_lines[i]
                        if re.search(date_pattern, potential_date_line) and not potential_date_line.startswith('●'):
                            duration = potential_date_line.strip()
                            i += 1
            else:
                i += 1
            
            # Collect bullet points (descriptions)
            while i < len(section_lines) and (section_lines[i].startswith('●') or 
                                             section_lines[i].startswith('•') or 
                                             section_lines[i].startswith('-')):
                bullet = section_lines[i].lstrip('●•-').strip()
                if bullet:  # Only add non-empty bullets
                    description.append(bullet)
                i += 1
            
            # Only add if we have at least a company or title
            if company or title:
                experience_list.append(Experience(
                    title=title,
                    company=company,
                    duration=duration,
                    description=description if description else None
                ))
        
        return experience_list
    
    def extract_skills_custom(self, text: str) -> List[str]:
        """Custom skills extraction"""
        skills = []
        lines = text.split('\n')
        
        start_idx, end_idx = self.find_section_bounds(text, ['TECHNICAL SKILLS', 'SKILLS'])
        
        if start_idx is None:
            return skills
        
        section_lines = [lines[i].strip() for i in range(start_idx, end_idx) if lines[i].strip()]
        
        for line in section_lines:
            line = line.lstrip('●•-').strip()
            
            if not line:
                continue
            
            # Split by category (e.g., "Languages: Java, Python")
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    skill_list = parts[1].split(',')
                    for skill in skill_list:
                        skill = skill.strip()
                        if skill:
                            skills.append(skill)
            else:
                # Comma-separated
                if ',' in line:
                    skill_list = line.split(',')
                    for skill in skill_list:
                        skill = skill.strip()
                        if skill:
                            skills.append(skill)
                else:
                    if len(line) < 100:
                        skills.append(line)
        
        return skills
    
    def parse(self, pdf_path: str, debug: bool = False) -> ParsedResume:
        """
        Parse resume using pyresparser if available, otherwise use custom parsing
        """
        if debug:
            print("=" * 70)
            print(f"Using pyresparser: {self.use_pyresparser}")
            print(f"Using pdfminer3: {self.use_pdfminer}")
            print("=" * 70)
        
        # Extract raw text and page count
        text = self.extract_text_from_pdf(pdf_path)
        total_pages = self.count_pdf_pages(pdf_path)
        
        if debug:
            print(f"\nTotal pages: {total_pages}")
            print(f"Text length: {len(text)} characters")
            print("\nFirst 500 characters:")
            print(text[:500])
            print("\n")
        
        # Try pyresparser first if available
        if self.use_pyresparser:
            try:
                if debug:
                    print("Attempting to use pyresparser...")
                
                resume_data = PyResumeParser(pdf_path).get_extracted_data()
                
                # Extract contact info from pyresparser
                contact = ContactInfo(
                    name=resume_data.get('name'),
                    email=resume_data.get('email'),
                    phone=resume_data.get('mobile_number'),
                    linkedin=None,  # pyresparser doesn't extract this reliably
                    github=None
                )
                
                # Get skills from pyresparser
                skills = resume_data.get('skills', [])
                
                # Get education from pyresparser (if available) or use custom
                education = []
                if resume_data.get('degree'):
                    # pyresparser found education
                    for i, degree in enumerate(resume_data.get('degree', [])):
                        institution = resume_data.get('college_name', [''])[i] if i < len(resume_data.get('college_name', [])) else ''
                        education.append(Education(
                            degree=degree,
                            institution=institution,
                            year=None,
                            additional_info=None
                        ))
                
                # If pyresparser didn't find education, use custom parser
                if not education:
                    education = self.extract_education_custom(text)
                
                # pyresparser doesn't extract experience well, use custom
                experience = self.extract_experience_custom(text)
                
                # Extract LinkedIn and GitHub from raw text
                linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
                github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w-]+'
                
                linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
                github_match = re.search(github_pattern, text, re.IGNORECASE)
                
                if linkedin_match:
                    contact.linkedin = linkedin_match.group(0)
                elif 'linkedin' in text.lower():
                    contact.linkedin = "LinkedIn profile mentioned"
                
                if github_match:
                    contact.github = github_match.group(0)
                elif 'github' in text.lower():
                    contact.github = "GitHub profile mentioned"
                
                # If skills are empty, try custom extraction
                if not skills:
                    skills = self.extract_skills_custom(text)
                
                if debug:
                    print(f"✓ pyresparser successful")
                    print(f"  Name: {contact.name}")
                    print(f"  Email: {contact.email}")
                    print(f"  Skills: {len(skills)}")
                    print(f"  Education: {len(education)}")
                    print(f"  Experience: {len(experience)}")
                
                return ParsedResume(
                    contact=contact,
                    skills=skills,
                    education=education,
                    experience=experience,
                    raw_text=text,
                    total_pages=total_pages
                )
            
            except Exception as e:
                if debug:
                    print(f"pyresparser failed: {e}")
                    print("Falling back to custom parser...")
        
        # Fallback to custom parsing
        if debug:
            print("Using custom parser...")
        
        # Extract contact info
        # Try to find name - check first few lines
        name = None
        first_lines = text.split('\n')[:5]
        for line in first_lines:
            line = line.strip()
            # Skip lines with email or phone
            if '@' in line or re.search(r'\d{3}[-.\s]?\d{3}', line):
                continue
            # Look for name pattern (2-4 words, can be all caps or title case)
            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if it's likely a name (not too long, no special chars)
                if all(w.replace('.', '').replace(',', '').isalpha() for w in words):
                    name = line
                    break
        
        if not name:
            # Fallback to first line
            name = first_lines[0].strip() if first_lines else None
        
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/[\w-]+', text, re.IGNORECASE)
        
        # Extract location from first few lines
        location = None
        for line in first_lines:
            location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})', line)
            if location_match:
                location = f"{location_match.group(1)}, {location_match.group(2)}"
                break
        
        contact = ContactInfo(
            name=name,
            email=email_match.group(0) if email_match else None,
            phone=phone_match.group(0) if phone_match else None,
            linkedin=linkedin_match.group(0) if linkedin_match else ("LinkedIn profile mentioned" if 'linkedin' in text.lower() else None),
            github=github_match.group(0) if github_match else ("GitHub profile mentioned" if 'github' in text.lower() else None),
            location=location
        )
        
        # Extract sections
        skills = self.extract_skills_custom(text)
        education = self.extract_education_custom(text)
        experience = self.extract_experience_custom(text)
        
        if debug:
            print(f"  Name: {contact.name}")
            print(f"  Email: {contact.email}")
            print(f"  Skills: {len(skills)}")
            print(f"  Education: {len(education)}")
            print(f"  Experience: {len(experience)}")
        
        return ParsedResume(
            contact=contact,
            skills=skills,
            education=education,
            experience=experience,
            raw_text=text,
            total_pages=total_pages
        )
    
    def parse_to_dict(self, pdf_path: str) -> Dict:
        """Parse resume and return as dictionary"""
        parsed = self.parse(pdf_path)
        return {
            'contact': asdict(parsed.contact),
            'skills': parsed.skills,
            'education': [asdict(edu) for edu in parsed.education],
            'experience': [asdict(exp) for exp in parsed.experience],
            'total_pages': parsed.total_pages
        }
    
    def parse_to_json(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        """Parse resume and return/save as JSON"""
        data = self.parse_to_dict(pdf_path)
        json_str = json.dumps(data, indent=2)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_str)
        
        return json_str


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python resume_parser_final.py <path_to_resume.pdf> [--debug]")
        print("Example: python resume_parser_final.py resume.pdf")
        print("         python resume_parser_final.py resume.pdf --debug")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    debug = '--debug' in sys.argv
    
    if not Path(pdf_path).exists():
        print(f"Error: File '{pdf_path}' not found")
        sys.exit(1)
    
    # Parse resume
    parser = FinalResumeParser()
    print(f"Parsing resume: {pdf_path}\n")
    
    try:
        result = parser.parse_to_dict(pdf_path)
        
        # If debug mode, parse again with debug output
        if debug:
            parser.parse(pdf_path, debug=True)
        
        # Pretty print results
        print("=" * 70)
        print("PARSED RESUME")
        print("=" * 70)
        
        print("\nCONTACT INFORMATION:")
        print("-" * 70)
        for key, value in result['contact'].items():
            if value:
                print(f"{key.capitalize()}: {value}")
        
        print(f"\nTOTAL PAGES: {result['total_pages']}")
        
        print("\nSKILLS:")
        print("-" * 70)
        if result['skills']:
            for i, skill in enumerate(result['skills'], 1):
                print(f"  {i}. {skill}")
        else:
            print("  ❌ No skills detected")
        
        print("\nEDUCATION:")
        print("-" * 70)
        if result['education']:
            for i, edu in enumerate(result['education'], 1):
                print(f"\n  {i}. {edu['institution']}")
                print(f"     Degree: {edu['degree']}")
                if edu['year']:
                    print(f"     Year: {edu['year']}")
                if edu['additional_info']:
                    print(f"     Info: {edu['additional_info']}")
        else:
            print("  ❌ No education detected")
        
        print("\nEXPERIENCE:")
        print("-" * 70)
        if result['experience']:
            for i, exp in enumerate(result['experience'], 1):
                print(f"\n  {i}. {exp['company']}")
                print(f"     Title: {exp['title']}")
                if exp['duration']:
                    print(f"     Duration: {exp['duration']}")
                if exp['description']:
                    print(f"     Responsibilities ({len(exp['description'])} items):")
                    for desc in exp['description'][:2]:  # Show first 2
                        preview = desc[:80] + "..." if len(desc) > 80 else desc
                        print(f"       • {preview}")
                    if len(exp['description']) > 2:
                        print(f"       ... and {len(exp['description']) - 2} more")
        else:
            print("  ❌ No experience detected")
        
        # Save to JSON
        output_file = pdf_path.replace('.pdf', '_parsed.json')
        parser.parse_to_json(pdf_path, output_file)
        print(f"\n{'=' * 70}")
        print(f"✓ JSON output saved to: {output_file}")
        print("=" * 70)
        
        if not result['education'] or not result['experience']:
            print("\n" + "!" * 70)
            print("TIP: If sections weren't detected, try:")
            print(f"  1. Run with --debug flag: python resume_parser_final.py {pdf_path} --debug")
            print(f"  2. Install pyresparser for better results: pip install pyresparser")
            print(f"  3. Install pdfminer3 for better text extraction: pip install pdfminer3")
            print("!" * 70)
        
    except Exception as e:
        print(f"Error parsing resume: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()