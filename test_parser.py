"""
Test script for resume parser
Run this to verify the parser is working
"""

from resume_parser import ResumeParser, ContactInfo, Education, Experience
import json


def test_email_extraction():
    """Test email extraction"""
    parser = ResumeParser()
    
    test_cases = [
        ("Contact me at john.doe@email.com", "john.doe@email.com"),
        ("Email: jane_smith123@company.org", "jane_smith123@company.org"),
        ("reach out: test+tag@domain.co.uk", "test+tag@domain.co.uk"),
    ]
    
    print("Testing email extraction...")
    for text, expected in test_cases:
        result = parser.extract_email(text)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{text}' -> {result}")


def test_phone_extraction():
    """Test phone number extraction"""
    parser = ResumeParser()
    
    test_cases = [
        "Call me at (123) 456-7890",
        "Phone: 123-456-7890",
        "Mobile: 123.456.7890",
        "+1 123 456 7890"
    ]
    
    print("\nTesting phone extraction...")
    for text in test_cases:
        result = parser.extract_phone(text)
        status = "✓" if result else "✗"
        print(f"  {status} '{text}' -> {result}")


def test_linkedin_extraction():
    """Test LinkedIn URL extraction"""
    parser = ResumeParser()
    
    test_cases = [
        "LinkedIn: linkedin.com/in/johndoe",
        "https://www.linkedin.com/in/jane-smith",
        "Connect with me: www.linkedin.com/in/developer123"
    ]
    
    print("\nTesting LinkedIn extraction...")
    for text in test_cases:
        result = parser.extract_linkedin(text)
        status = "✓" if result else "✗"
        print(f"  {status} '{text}' -> {result}")


def test_github_extraction():
    """Test GitHub URL extraction"""
    parser = ResumeParser()
    
    test_cases = [
        "GitHub: github.com/johndoe",
        "https://github.com/developer123",
        "Code: www.github.com/awesome-dev"
    ]
    
    print("\nTesting GitHub extraction...")
    for text in test_cases:
        result = parser.extract_github(text)
        status = "✓" if result else "✗"
        print(f"  {status} '{text}' -> {result}")


def test_skills_extraction():
    """Test skills extraction"""
    parser = ResumeParser()
    
    test_text = """
    SKILLS
    • Python, Java, JavaScript
    • React, Node.js, Django
    • AWS, Docker, Kubernetes
    • Machine Learning, TensorFlow
    """
    
    print("\nTesting skills extraction...")
    skills = parser.extract_skills(test_text)
    print(f"  Found {len(skills)} skills:")
    for skill in skills[:10]:  # Show first 10
        print(f"    • {skill}")


def test_section_extraction():
    """Test section extraction"""
    parser = ResumeParser()
    
    test_text = """
    John Doe
    
    EXPERIENCE
    Software Engineer at Tech Corp
    Developed cool stuff
    
    EDUCATION
    BS Computer Science
    University Name
    
    SKILLS
    Python, Java
    """
    
    print("\nTesting section extraction...")
    
    exp_section = parser._extract_section(test_text, 'experience')
    edu_section = parser._extract_section(test_text, 'education')
    skills_section = parser._extract_section(test_text, 'skills')
    
    print(f"  {'✓' if exp_section else '✗'} Experience section: {'Found' if exp_section else 'Not found'}")
    print(f"  {'✓' if edu_section else '✗'} Education section: {'Found' if edu_section else 'Not found'}")
    print(f"  {'✓' if skills_section else '✗'} Skills section: {'Found' if skills_section else 'Not found'}")


def test_data_structures():
    """Test data structures"""
    print("\nTesting data structures...")
    
    contact = ContactInfo(
        name="John Doe",
        email="john@email.com",
        phone="123-456-7890"
    )
    
    edu = Education(
        degree="BS Computer Science",
        institution="MIT",
        year="2020",
        gpa="3.8"
    )
    
    exp = Experience(
        title="Software Engineer",
        company="Google",
        duration="2020-2023",
        description="Built awesome things"
    )
    
    print("  ✓ ContactInfo created")
    print("  ✓ Education created")
    print("  ✓ Experience created")
    
    # Test serialization
    import dataclasses
    contact_dict = dataclasses.asdict(contact)
    print(f"  ✓ Serialization works: {contact_dict['name']}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("RESUME PARSER TESTS")
    print("=" * 60)
    
    test_email_extraction()
    test_phone_extraction()
    test_linkedin_extraction()
    test_github_extraction()
    test_skills_extraction()
    test_section_extraction()
    test_data_structures()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)
    print("\nTo test with a real PDF, run:")
    print("  python resume_parser.py your_resume.pdf")


if __name__ == "__main__":
    main()