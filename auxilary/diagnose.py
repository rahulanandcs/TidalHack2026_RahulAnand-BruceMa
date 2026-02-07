"""
Resume Parser Diagnostic Tool
Use this to debug why sections aren't being detected
"""

import sys
from pathlib import Path
from archive import ResumeParser


def diagnose_resume(pdf_path: str):
    """Run diagnostics on a resume PDF"""
    
    if not Path(pdf_path).exists():
        print(f"Error: File '{pdf_path}' not found")
        return
    
    parser = ResumeParser()
    
    print("=" * 70)
    print("RESUME PARSER DIAGNOSTICS")
    print("=" * 70)
    print(f"File: {pdf_path}\n")
    
    # Extract raw text
    try:
        text = parser.extract_text_from_pdf(pdf_path)
    except Exception as e:
        print(f"❌ ERROR: Could not read PDF: {e}")
        return
    
    print("✓ PDF successfully read")
    print(f"✓ Total text length: {len(text)} characters")
    print(f"✓ Total lines: {len(text.split(chr(10)))}\n")
    
    # Show first 1000 characters
    print("=" * 70)
    print("EXTRACTED TEXT (first 1000 characters)")
    print("=" * 70)
    print(text[:1000])
    print("...\n")
    
    # Check for section headers
    print("=" * 70)
    print("SECTION HEADER DETECTION")
    print("=" * 70)
    
    text_lower = text.lower()
    lines_lower = [l.lower().strip() for l in text.split('\n')]
    
    all_sections = {
        'Experience': ['experience', 'work experience', 'employment', 'work history', 'professional experience'],
        'Education': ['education', 'academic', 'qualification'],
        'Skills': ['skills', 'technical skills', 'core competencies', 'expertise', 'technologies'],
        'Projects': ['projects', 'personal projects', 'key projects']
    }
    
    for section_name, headers in all_sections.items():
        print(f"\n{section_name} section:")
        found = False
        for header in headers:
            if header in text_lower:
                # Find which line it's on
                for i, line in enumerate(lines_lower):
                    if header in line and len(line) < 50:
                        print(f"  ✓ Found '{header}' on line {i}: '{text.split(chr(10))[i].strip()}'")
                        found = True
                        break
        if not found:
            print(f"  ❌ Not found. Searched for: {', '.join(headers)}")
    
    # Try to extract sections
    print("\n" + "=" * 70)
    print("SECTION EXTRACTION RESULTS")
    print("=" * 70)
    
    for section_type in ['experience', 'education', 'skills']:
        section = parser._extract_section(text, section_type)
        if section:
            print(f"\n✓ {section_type.upper()} section extracted ({len(section)} chars)")
            print(f"Preview (first 300 chars):")
            print("-" * 70)
            print(section[:300])
            if len(section) > 300:
                print("...")
        else:
            print(f"\n❌ {section_type.upper()} section NOT extracted")
    
    # Test parsing
    print("\n" + "=" * 70)
    print("PARSING RESULTS")
    print("=" * 70)
    
    result = parser.parse_to_dict(pdf_path)
    
    print(f"\nContact Info:")
    print(f"  Name: {result['contact']['name']}")
    print(f"  Email: {result['contact']['email']}")
    print(f"  Phone: {result['contact']['phone']}")
    
    print(f"\nSkills: {len(result['skills'])} found")
    if result['skills']:
        print(f"  {', '.join(result['skills'][:10])}")
    
    print(f"\nEducation: {len(result['education'])} entries found")
    for edu in result['education']:
        print(f"  • {edu['degree']}")
        if edu['institution']:
            print(f"    {edu['institution']}")
    
    print(f"\nExperience: {len(result['experience'])} entries found")
    for exp in result['experience']:
        print(f"  • {exp['title']}")
        if exp['company']:
            print(f"    Company: {exp['company']}")
        if exp['duration']:
            print(f"    Duration: {exp['duration']}")
    
    # Suggestions
    print("\n" + "=" * 70)
    print("SUGGESTIONS")
    print("=" * 70)
    
    if not result['education']:
        print("\n❌ No education detected. Common issues:")
        print("  1. Section header might use different wording (e.g., 'Academic Background')")
        print("  2. Degree keywords not recognized (add to COMMON_SKILLS in parser)")
        print("  3. Section might not be clearly separated from other content")
        print("\n  Try manually checking the extracted text above for education content.")
    
    if not result['experience']:
        print("\n❌ No experience detected. Common issues:")
        print("  1. Section header might use different wording (e.g., 'Professional Background')")
        print("  2. Jobs might not have clear date ranges")
        print("  3. Format might be unusual (e.g., no bullets, unconventional layout)")
        print("\n  Try manually checking the extracted text above for experience content.")
    
    if not result['skills']:
        print("\n❌ No skills detected. Common issues:")
        print("  1. Skills section not clearly labeled")
        print("  2. Skills not matching the predefined list")
        print("  3. Skills in unusual format")
        print("\n  You can add custom skills to COMMON_SKILLS in resume_parser.py")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Review the 'EXTRACTED TEXT' section above")
    print("2. Check if section headers match those being searched for")
    print("3. Modify SECTION_HEADERS in resume_parser.py if needed")
    print("4. For custom resume formats, you may need to adjust the parsing logic")
    print("\nTip: Save the raw extracted text to a file for easier review:")
    print(f"    python -c \"from resume_parser import ResumeParser; p = ResumeParser(); print(p.extract_text_from_pdf('{pdf_path}'))\" > extracted_text.txt")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose.py <path_to_resume.pdf>")
        print("Example: python diagnose.py resume.pdf")
        sys.exit(1)
    
    diagnose_resume(sys.argv[1])
