"""
Career Fair Employer Web Scraper
Extracts employer information from TAMU HireAggies career fair pages
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
from datetime import datetime


class CareerFairScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with Chrome WebDriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def scrape_employer_page(self, url):
        """
        Scrape employer information from a career fair page
        
        Args:
            url: The employer page URL
            
        Returns:
            dict: Dictionary containing all extracted employer information
        """
        print(f"Fetching URL: {url}")
        self.driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        employer_data = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'company_name': None,
            'about': None,
            'we_are_looking_for': None,
            'organization_profile': {},
            'event_details': {},
            'all_text_content': None
        }

        try:
            
            # Extract company name
            try:
                # Try multiple selectors for company name
                company_selectors = ['h3', 'h1', '.company-name', '.employer-name', '.flex-auto']
                for selector in company_selectors:
                    try:
                        company_name = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if company_name.text.strip():
                            employer_data['company_name'] = company_name.text.strip()
                            print(f"Company name found: {employer_data['company_name']}")
                            break
                    except NoSuchElementException:
                        continue
            except Exception as e:
                print(f"Error finding company name: {e}")
            
    

            # Extract all section headings and their content
            sections = self.extract_sections()
            
            # If we didn't get many sections, try alternative extraction method
            if len(sections) < 3:
                print("\n⚠ Few sections found, trying alternative extraction...")
                alt_sections = self.extract_sections_alternative()
                sections.update(alt_sections)
            
            # Process specific sections
            for section_title, section_content in sections.items():
                title_lower = section_title.lower()
                
                if 'about' in title_lower and not 'looking' in title_lower:
                    employer_data['about'] = section_content
                elif 'looking for' in title_lower or 'we are looking' in title_lower:
                    employer_data['we_are_looking_for'] = section_content
                elif 'organization profile' in title_lower or 'company profile' in title_lower:
                    employer_data['organization_profile'] = self.parse_profile_section(section_content)
                elif 'event' in title_lower or 'booth' in title_lower:
                    employer_data['event_details'] = self.parse_profile_section(section_content)
                elif 'contact' in title_lower:
                    employer_data['contact_info'] = self.parse_profile_section(section_content)
            
            # Extract structured data fields
            employer_data.update(self.extract_structured_fields())
            
            # Get all text content from the page
            employer_data['all_text_content'] = self.driver.find_element(By.TAG_NAME, 'body').text
            
            # Store all sections
            employer_data['all_sections'] = sections
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            employer_data['error'] = str(e)
        
        return employer_data
    
    def extract_sections(self):
        """Extract all sections with headings and their content"""
        sections = {}
        
        try:
            # Try multiple heading selectors - cast a more inclusive net
            heading_selectors = [
                'h2',
                '.fg-title', 'fg-title'
            ]
            
            headings = []
            for selector in heading_selectors:
                try:
                    found = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    headings.extend(found)
                except:
                    continue
            
            # Remove duplicates while preserving order
            seen = set()
            unique_headings = []
            for heading in headings:
                if heading not in seen:
                    seen.add(heading)
                    unique_headings.append(heading)
            
            print(f"\nFound {len(unique_headings)} unique headings")
            
            for heading in unique_headings:
                try:
                    title = heading.text.strip()
                    if not title:
                        continue
                    
                    print(f"\n→ Processing heading: '{title}'")
                    
                    # Get content after this heading
                    content = self.get_content_after_heading(heading)
                    if content:
                        sections[title] = content
                        print(f"  ✓ Got content ({len(content)} chars)")
                    else:
                        print(f"  ✗ No content found")
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error extracting sections: {e}")
        
        return sections
    
    def extract_sections_alternative(self):
        """Alternative method: look for section containers with title and content"""
        sections = {}
        
        try:
            # Look for common section container patterns
            container_selectors = [
                'section',
                'div.section',
                'div[class*="section"]',
                'div[class*="panel"]',
                'div[class*="card"]',
                'div[class*="box"]'
            ]
            
            for selector in container_selectors:
                try:
                    containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for container in containers:
                        # Try to find a title within this container
                        title = None
                        content = None
                        
                        try:
                            title_elem = container.find_element(
                                By.CSS_SELECTOR, 
                                'h2, h3, h4, .title, .heading, [class*="title"]'
                            )
                            title = title_elem.text.strip()
                        except:
                            pass
                        
                        if title:
                            # Get all text from container except the title
                            container_text = container.text.strip()
                            if container_text.startswith(title):
                                content = container_text[len(title):].strip()
                            else:
                                content = container_text
                            
                            if content and title not in sections:
                                sections[title] = content
                                print(f"  ✓ Alternative method found: '{title}' ({len(content)} chars)")
                                
                except:
                    continue
                    
        except Exception as e:
            print(f"Error in alternative extraction: {e}")
        
        return sections
    
    def get_content_after_heading(self, heading_element):
        """Get the content that follows a heading element"""
        try:
            content_parts = []
            
            # Strategy 1: Try sibling traversal from the heading itself
            current_elem = heading_element
            found_content = False
            
            while True:
                try:
                    # Get next sibling
                    next_elem = current_elem.find_element(By.XPATH, './following-sibling::*[1]')
                    
                    # Check if this element has class 'list-border'
                    elem_classes = next_elem.get_attribute('class') or ''
                    if 'list-border' in elem_classes:
                        # Stop when we hit the list-border
                        break
                    
                    # Check if this is another heading (stop before next section)
                    tag_name = next_elem.tag_name.lower()
                    if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break
                    if 'title' in elem_classes or 'heading' in elem_classes:
                        break
                    
                    # Add this element's text to our content
                    elem_text = next_elem.text.strip()
                    if elem_text:
                        content_parts.append(elem_text)
                        found_content = True
                    
                    # Move to the next element
                    current_elem = next_elem
                    
                except NoSuchElementException:
                    # No more siblings, stop iterating
                    break
            
            # Strategy 2: If no content found, try parent's siblings
            if not found_content:
                try:
                    parent = heading_element.find_element(By.XPATH, './..')
                    current_elem = parent
                    
                    while True:
                        try:
                            next_elem = current_elem.find_element(By.XPATH, './following-sibling::*[1]')
                            
                            elem_classes = next_elem.get_attribute('class') or ''
                            if 'list-border' in elem_classes:
                                break
                            
                            # Check if this is another section container
                            tag_name = next_elem.tag_name.lower()
                            if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                                break
                            
                            elem_text = next_elem.text.strip()
                            if elem_text:
                                content_parts.append(elem_text)
                            
                            current_elem = next_elem
                        except NoSuchElementException:
                            break
                except:
                    pass
            
            # Strategy 3: If still no content, try looking for next div/p elements
            if not content_parts:
                try:
                    # Look for content elements after the heading
                    following_elements = heading_element.find_elements(
                        By.XPATH, 
                        './following::*[self::div or self::p or self::ul or self::ol][position() <= 10]'
                    )
                    
                    for elem in following_elements:
                        elem_classes = elem.get_attribute('class') or ''
                        if 'list-border' in elem_classes:
                            break
                        
                        # Check if we've gone too far (hit another heading)
                        tag_name = elem.tag_name.lower()
                        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            break
                        
                        elem_text = elem.text.strip()
                        if elem_text and elem_text not in content_parts:
                            content_parts.append(elem_text)
                            if len(content_parts) >= 3:  # Limit to avoid grabbing too much
                                break
                except:
                    pass
            
            result = '\n'.join(content_parts) if content_parts else None
            if result:
                print(f"    Content preview: {result[:100]}...")
            else:
                print(f"    No content found")
            
            return result
            
        except Exception as e:
            print(f"    Exception in get_content_after_heading: {e}")
            return None 
    
    def extract_structured_fields(self):
        """Extract specific structured data fields like majors, class years, etc."""
        structured_data = {
            'industry': None,
            'website': None,
            'position_types': [],
            'majors_recruited': [],
            'desired_class_years': [],
            'booth_location': None,
            'contact_info': {}
        }
        
        try:
            # Look for labeled fields
            labels = self.driver.find_elements(By.CSS_SELECTOR, 'label, .label, .field-label, dt, strong, b')
            
            for label in labels:
                try:
                    label_text = label.text.strip().lower().replace(':', '')
                    
                    # Try to find the associated value
                    value = self.get_value_for_label(label)
                    
                    if not value:
                        continue
                    
                    # Map to structured fields
                    if 'industry' in label_text or 'industries' in label_text:
                        structured_data['industry'] = value
                    elif 'website' in label_text or 'url' in label_text:
                        structured_data['website'] = value
                    elif 'position' in label_text and 'type' in label_text:
                        structured_data['position_types'] = self.parse_list_field(value)
                    elif 'major' in label_text and 'recruit' in label_text:
                        structured_data['majors_recruited'] = self.parse_list_field(value)
                    elif 'class' in label_text and 'year' in label_text:
                        structured_data['desired_class_years'] = self.parse_list_field(value)
                    elif 'booth' in label_text and 'location' in label_text:
                        structured_data['booth_location'] = value
                    elif any(keyword in label_text for keyword in ['email', 'phone', 'contact']):
                        structured_data['contact_info'][label_text] = value
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error extracting structured fields: {e}")
        
        return structured_data
    
    def get_value_for_label(self, label_element):
        """Get the value associated with a label element"""
        try:
            # Try next sibling
            next_elem = label_element.find_element(By.XPATH, './following-sibling::*[1]')
            return next_elem.text.strip()
        except:
            try:
                # Try parent's next sibling
                parent = label_element.find_element(By.XPATH, './..')
                next_elem = parent.find_element(By.XPATH, './following-sibling::*[1]')
                return next_elem.text.strip()
            except:
                try:
                    # Try dd element (for dl/dt/dd lists)
                    dd = label_element.find_element(By.XPATH, './following-sibling::dd[1]')
                    return dd.text.strip()
                except:
                    return None
    
    def parse_list_field(self, value):
        """Parse a comma-separated or newline-separated list field"""
        if not value:
            return []
        
        # Try comma separation first
        if ',' in value:
            return [item.strip() for item in value.split(',') if item.strip()]
        # Try newline separation
        elif '\n' in value:
            return [item.strip() for item in value.split('\n') if item.strip()]
        # Single value
        else:
            return [value.strip()]
    
    def parse_profile_section(self, content):
        """Parse a profile section that might have key-value pairs"""
        profile = {}
        
        if not content:
            return profile
        
        lines = content.split('\n')
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    profile[key] = value
            else:
                # Store non-key-value content
                if 'content' not in profile:
                    profile['content'] = []
                profile['content'].append(line.strip())
        
        return profile
    
    def save_to_json(self, data, filename='employer_data.json'):
        """Save the scraped data to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()


def main():
    """Example usage"""
    # The URL you provided
    url = "https://tamu-csm.symplicity.com/students/app/career-fairs/4e14310febad2eb8767770a213251a7f/employers/01f5016d99e193977c1bf344ba0b0a15"
    
    # Create scraper instance
    scraper = CareerFairScraper(headless=True)
    
    try:
        # Scrape the employer page
        employer_data = scraper.scrape_employer_page(url)
        
        # Print the results
        print("\n" + "="*80)
        print("SCRAPED DATA")
        print("="*80)
        print(json.dumps(employer_data, indent=2))
        
        # Save to file
        scraper.save_to_json(employer_data, 'employer_data.json')
        
    finally:
        # Clean up
        scraper.close()


if __name__ == "__main__":
    main()