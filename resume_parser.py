"""
Resume Parser - Extracts structured data from PDF resumes
Supports: Contact info, Skills, Education, Experience
"""

import re
import PyPDF2
from pathlib import Path
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


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


@dataclass
class Experience:
    """Work experience entry"""
    title: str
    company: str
    duration: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ParsedResume:
    """Complete parsed resume data"""
    contact: ContactInfo
    skills: List[str]
    education: List[Education]
    experience: List[Experience]
    raw_text: str


class ResumeParser:
    """Main resume parser class"""
    
    # Common skill keywords (expand this list based on your needs)
    COMMON_SKILLS = {
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'fastapi',
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
        'git', 'ci/cd', 'jenkins', 'github actions',
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
        'html', 'css', 'sass', 'tailwind',
        'rest api', 'graphql', 'microservices',
        'agile', 'scrum', 'jira',
        'linux', 'bash', 'shell scripting'
    }
    
    # Section headers to identify resume sections
    SECTION_HEADERS = {
        'experience': ['experience', 'work experience', 'employment', 'work history', 'professional experience'],
        'education': ['education', 'academic', 'qualification'],
        'skills': ['skills', 'technical skills', 'core competencies', 'expertise', 'technologies'],
        'projects': ['projects', 'personal projects', 'key projects']
    }
    
    def __init__(self):
        """Initialize the parser"""
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return text
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        # Matches formats: (123) 456-7890, 123-456-7890, 123.456.7890, +1 123 456 7890
        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
        phones = re.findall(phone_pattern, text)
        # Filter out numbers that are too short or too long
        valid_phones = [p for p in phones if 10 <= len(re.sub(r'[^\d]', '', p)) <= 15]
        return valid_phones[0] if valid_phones else None
    
    def extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn URL from text"""
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
        matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        return matches[0] if matches else None
    
    def extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub URL from text"""
        github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w-]+'
        matches = re.findall(github_pattern, text, re.IGNORECASE)
        return matches[0] if matches else None
    
    def extract_name(self, text: str) -> Optional[str]:
        """
        Extract name from resume (usually first line or before contact info)
        This is a simple heuristic - may need refinement
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # Usually name is in the first few lines and is short
            for line in lines[:5]:
                # Skip lines with email or phone
                if '@' in line or re.search(r'\d{3}[-.\s]?\d{3}', line):
                    continue
                # Name is typically 2-4 words, each capitalized
                words = line.split()
                if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                    return line
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text
        Looks for skills section and common technical keywords
        """
        skills = set()
        text_lower = text.lower()
        
        # Find skills section
        skills_section = self._extract_section(text, 'skills')
        
        if skills_section:
            # Look for skills in the skills section
            for skill in self.COMMON_SKILLS:
                if skill in skills_section.lower():
                    skills.add(skill)
            
            # Also extract comma-separated or bullet-pointed skills
            # Match patterns like "• Python" or "- JavaScript" or "Python, Java"
            skill_lines = re.findall(r'[•\-\*]\s*([A-Za-z0-9+#\.\s]+?)(?:\n|,|$)', skills_section)
            for skill in skill_lines:
                skill = skill.strip()
                if skill and len(skill) < 50:  # Avoid long descriptions
                    skills.add(skill)
        
        # Also scan entire document for common skills
        for skill in self.COMMON_SKILLS:
            if skill in text_lower:
                skills.add(skill)
        
        return sorted(list(skills))
    
    def _extract_section(self, text: str, section_type: str) -> Optional[str]:
        """
        Extract a specific section from resume text
        
        Args:
            text: Full resume text
            section_type: Type of section ('experience', 'education', 'skills', etc.)
            
        Returns:
            Text of that section or None
        """
        headers = self.SECTION_HEADERS.get(section_type, [])
        text_lower = text.lower()
        
        for header in headers:
            # Find the header
            pattern = rf'\n\s*{re.escape(header)}\s*\n'
            match = re.search(pattern, text_lower)
            if match:
                start_idx = match.end()
                
                # Find the next section header
                next_section_idx = len(text)
                for other_type, other_headers in self.SECTION_HEADERS.items():
                    if other_type == section_type:
                        continue
                    for other_header in other_headers:
                        pattern = rf'\n\s*{re.escape(other_header)}\s*\n'
                        next_match = re.search(pattern, text_lower[start_idx:])
                        if next_match:
                            potential_end = start_idx + next_match.start()
                            next_section_idx = min(next_section_idx, potential_end)
                
                return text[start_idx:next_section_idx].strip()
        
        return None
    
    def extract_education(self, text: str) -> List[Education]:
        """Extract education information"""
        education_list = []
        education_section = self._extract_section(text, 'education')
        
        if not education_section:
            return education_list
        
        # Common degree patterns
        degree_patterns = [
            r'(Bachelor|Master|Ph\.?D\.?|B\.S\.?|M\.S\.?|B\.A\.?|M\.A\.?|MBA|Associate)',
            r'(Computer Science|Engineering|Business|Mathematics|Physics|Chemistry|Biology)',
        ]
        
        # Split by lines and look for degree/institution pairs
        lines = education_section.split('\n')
        current_edu = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains a degree
            for pattern in degree_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if current_edu:
                        education_list.append(current_edu)
                    current_edu = Education(degree=line, institution="")
                    break
            
            # Look for years (graduation year)
            year_match = re.search(r'(19|20)\d{2}', line)
            if year_match and current_edu:
                current_edu.year = year_match.group(0)
            
            # Look for GPA
            gpa_match = re.search(r'GPA:?\s*(\d\.\d+)', line, re.IGNORECASE)
            if gpa_match and current_edu:
                current_edu.gpa = gpa_match.group(1)
            
            # If line doesn't match degree but we have current_edu, it might be institution
            if current_edu and not current_edu.institution and not re.search(r'(19|20)\d{2}', line):
                if len(line) > 5 and not line.startswith('•') and not line.startswith('-'):
                    current_edu.institution = line
        
        if current_edu:
            education_list.append(current_edu)
        
        return education_list
    
    def extract_experience(self, text: str) -> List[Experience]:
        """Extract work experience"""
        experience_list = []
        experience_section = self._extract_section(text, 'experience')
        
        if not experience_section:
            return experience_list
        
        # Split into potential job entries (separated by blank lines or dates)
        entries = re.split(r'\n\s*\n', experience_section)
        
        for entry in entries:
            if not entry.strip():
                continue
            
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            if not lines:
                continue
            
            # First line often contains title and/or company
            title = lines[0]
            company = ""
            duration = None
            description = ""
            
            # Look for company (often second line or in first line after |)
            if len(lines) > 1:
                company = lines[1]
            
            # Look for date ranges
            date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4})'
            for line in lines:
                if re.search(date_pattern, line):
                    duration = line
                    break
            
            # Remaining lines are description
            desc_lines = lines[2:] if len(lines) > 2 else []
            description = ' '.join(desc_lines)
            
            if title:
                experience_list.append(Experience(
                    title=title,
                    company=company,
                    duration=duration,
                    description=description[:200] if description else None  # Truncate long descriptions
                ))
        
        return experience_list
    
    def parse(self, pdf_path: str) -> ParsedResume:
        """
        Parse a resume PDF and extract structured information
        
        Args:
            pdf_path: Path to PDF resume file
            
        Returns:
            ParsedResume object with extracted data
        """
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        # Extract contact information
        contact = ContactInfo(
            name=self.extract_name(text),
            email=self.extract_email(text),
            phone=self.extract_phone(text),
            linkedin=self.extract_linkedin(text),
            github=self.extract_github(text)
        )
        
        # Extract other sections
        skills = self.extract_skills(text)
        education = self.extract_education(text)
        experience = self.extract_experience(text)
        
        return ParsedResume(
            contact=contact,
            skills=skills,
            education=education,
            experience=experience,
            raw_text=text
        )
    
    def parse_to_dict(self, pdf_path: str) -> Dict:
        """Parse resume and return as dictionary"""
        parsed = self.parse(pdf_path)
        return {
            'contact': asdict(parsed.contact),
            'skills': parsed.skills,
            'education': [asdict(edu) for edu in parsed.education],
            'experience': [asdict(exp) for exp in parsed.experience]
        }
    
    def parse_to_json(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        """
        Parse resume and return/save as JSON
        
        Args:
            pdf_path: Path to PDF resume
            output_path: Optional path to save JSON file
            
        Returns:
            JSON string
        """
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
        print("Usage: python resume_parser.py <path_to_resume.pdf>")
        print("Example: python resume_parser.py resume.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"Error: File '{pdf_path}' not found")
        sys.exit(1)
    
    # Parse resume
    parser = ResumeParser()
    print(f"Parsing resume: {pdf_path}\n")
    
    try:
        result = parser.parse_to_dict(pdf_path)
        
        # Pretty print results
        print("=" * 60)
        print("PARSED RESUME")
        print("=" * 60)
        
        print("\nCONTACT INFORMATION:")
        print("-" * 60)
        for key, value in result['contact'].items():
            if value:
                print(f"{key.capitalize()}: {value}")
        
        print("\nSKILLS:")
        print("-" * 60)
        if result['skills']:
            for skill in result['skills']:
                print(f"  • {skill}")
        else:
            print("  No skills detected")
        
        print("\nEDUCATION:")
        print("-" * 60)
        if result['education']:
            for edu in result['education']:
                print(f"  • {edu['degree']}")
                if edu['institution']:
                    print(f"    {edu['institution']}")
                if edu['year']:
                    print(f"    Year: {edu['year']}")
                if edu['gpa']:
                    print(f"    GPA: {edu['gpa']}")
                print()
        else:
            print("  No education detected")
        
        print("\nEXPERIENCE:")
        print("-" * 60)
        if result['experience']:
            for exp in result['experience']:
                print(f"  • {exp['title']}")
                if exp['company']:
                    print(f"    {exp['company']}")
                if exp['duration']:
                    print(f"    {exp['duration']}")
                print()
        else:
            print("  No experience detected")
        
        # Save to JSON file
        output_file = pdf_path.replace('.pdf', '_parsed.json')
        parser.parse_to_json(pdf_path, output_file)
        print(f"\nJSON output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error parsing resume: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()