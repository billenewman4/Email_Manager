"""
Test script for Email Manager API endpoints.
This script tests both the /generate-email/student and /generate-email/b2bsales endpoints.
"""
import requests
import json
import argparse

# Base URL for the API
BASE_URL = "http://localhost:8080"  # Update this if your server is running on a different port/host

# Test data for student endpoint
STUDENT_TEST_DATA = {
    "user_info": {
        "name": "Alex Smith",
        "email": "alex.smith@example.com",
        "resume_content": """
            Education:
            Stanford University - Bachelor of Science in Computer Science (2018-2022)
            
            Experience:
            - Software Engineering Intern at Tech Corp (Summer 2021)
            - Research Assistant in NLP Lab (2020-2022)
            - Teaching Assistant for Introduction to Machine Learning (Fall 2021)
            
            Skills:
            Python, JavaScript, React, TensorFlow, PyTorch, NLP, Data Visualization
        """,
        "career_interest": "Machine Learning Engineering",
        "key_accomplishments": [
            "Published research paper on efficient transformer architectures",
            "Developed a chatbot that improved customer service response times by 40%",
            "Created an open-source library for data preprocessing with 1000+ GitHub stars"
        ]
    },
    "contact_info": {
        "name": "Jordan Lee",
        "company": "AI Innovations",
        "role": "Senior Machine Learning Engineer",
        "company_description": "AI Innovations is a leading company in developing cutting-edge artificial intelligence solutions for enterprise customers.",
        "location": "San Francisco, CA",
        "department": "Research & Development",
        "linkedin": "linkedin.com/in/jordan-lee-ai"
    },
    "max_searches": 1,
    "max_redrafts": 1
}

# Test data with custom template
STUDENT_TEST_DATA_WITH_TEMPLATE = {
    **STUDENT_TEST_DATA,
    "template": """
    Subject: Interested in discussing ML Engineering opportunities at {{company}}
    
    Dear {{name}},
    
    I hope this email finds you well. My name is {{sender_name}} and I'm a {{sender_background}}.
    
    I've been following {{company}}'s work in {{industry_focus}} and was particularly impressed by {{specific_company_achievement}}.
    
    Given my background in {{sender_expertise}}, I believe I could contribute to your team's goals. I would appreciate the opportunity to have a brief phone call to discuss how my skills might align with your needs.
    
    Would you be available for a 15-minute call next week?
    
    Thank you for your time and consideration.
    
    Best regards,
    {{sender_name}}
    """
}

# Test data for B2B sales endpoint
B2B_SALES_TEST_DATA = {
    "user_info": {
        "name": "Taylor Morgan",
        "email": "taylor.morgan@salescompany.com",
        "resume_content": """
            Experience:
            - Sales Director at Enterprise Solutions Inc (2018-Present)
            - Account Executive at Business Tech Co (2015-2018)
            - Sales Development Representative at SaaS Solutions (2013-2015)
            
            Skills:
            Solution Selling, Pipeline Management, CRM, Negotiation, Contract Management, Enterprise Sales
        """,
        "career_interest": "Enterprise Software Sales",
        "key_accomplishments": [
            "Exceeded sales targets by 150% for three consecutive years",
            "Closed $2.5M deal with Fortune 500 company",
            "Built and led a team of 12 account executives"
        ]
    },
    "contact_info": {
        "name": "Casey Kim",
        "company": "Tech Enterprise Corp",
        "role": "VP of Technology",
        "company_description": "Tech Enterprise Corp provides technology infrastructure solutions for global enterprises.",
        "location": "Chicago, IL",
        "department": "Technology",
        "linkedin": "linkedin.com/in/casey-kim-tech"
    },
    "max_searches": 1,
    "max_redrafts": 1
}

# B2B test data with custom template
B2B_SALES_TEST_DATA_WITH_TEMPLATE = {
    **B2B_SALES_TEST_DATA,
    "template": """
    Subject: Enhancing {{company}}'s Technology Infrastructure - Quick Call?
    
    Hello {{name}},
    
    I'm {{sender_name}} from {{sender_company}}, and I noticed {{company}} is leading in {{industry_focus}}.
    
    Our clients typically see {{benefit_1}} and {{benefit_2}} after implementing our solutions. Given your role as {{role}}, I thought you might be interested in how we could help {{company}} achieve similar results.
    
    Would you be open to a brief 15-minute call to discuss this further?
    
    Best regards,
    {{sender_name}}
    {{sender_title}}
    {{sender_contact}}
    """
}

def test_student_endpoint():
    """Test the /generate-email/student endpoint."""
    endpoint = f"{BASE_URL}/generate-email/student"
    
    print(f"Testing student endpoint: {endpoint}")
    print("Sending request with the following data:")
    print(f"User: {STUDENT_TEST_DATA['user_info']['name']}")
    print(f"Contact: {STUDENT_TEST_DATA['contact_info']['name']} at {STUDENT_TEST_DATA['contact_info']['company']}")
    
    try:
        response = requests.post(endpoint, json=STUDENT_TEST_DATA)
        response.raise_for_status()
        result = response.json()
        
        print("\n=== Student Endpoint Response ===")
        print(f"Status Code: {response.status_code}")
        print(f"Email Draft: {result.get('email_draft', 'No draft generated')[:200]}...")
        print(f"Email Sent: {result.get('email_sent', False)}")
        if not result.get('email_sent', False) and result.get('email_error'):
            print(f"Email Error: {result.get('email_error')}")
        print("=" * 50)
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error testing student endpoint: {str(e)}")
        return None

def test_b2b_sales_endpoint():
    """Test the /generate-email/b2bsales endpoint."""
    endpoint = f"{BASE_URL}/generate-email/b2bsales"
    
    print(f"Testing B2B sales endpoint: {endpoint}")
    print("Sending request with the following data:")
    print(f"User: {B2B_SALES_TEST_DATA['user_info']['name']}")
    print(f"Contact: {B2B_SALES_TEST_DATA['contact_info']['name']} at {B2B_SALES_TEST_DATA['contact_info']['company']}")
    
    try:
        response = requests.post(endpoint, json=B2B_SALES_TEST_DATA)
        
        print("\n=== B2B Sales Endpoint Response ===")
        print(f"Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response Content: {result}")
            
            if response.status_code == 200:
                print(f"Email Draft: {result.get('email_draft', 'No draft generated')[:200]}...")
                print(f"Email Sent: {result.get('email_sent', False)}")
                if not result.get('email_sent', False) and result.get('email_error'):
                    print(f"Email Error: {result.get('email_error')}")
            
            return result
        except Exception as json_err:
            print(f"Error parsing response as JSON: {str(json_err)}")
            print(f"Raw Response: {response.text[:500]}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {str(e)}")
        return None
    finally:
        print("=" * 50)

def test_student_endpoint_with_template():
    """Test the /generate-email/student endpoint with a custom template."""
    endpoint = f"{BASE_URL}/generate-email/student"
    
    print(f"Testing student endpoint with template: {endpoint}")
    print("Sending request with custom template")
    print(f"User: {STUDENT_TEST_DATA_WITH_TEMPLATE['user_info']['name']}")
    print(f"Contact: {STUDENT_TEST_DATA_WITH_TEMPLATE['contact_info']['name']} at {STUDENT_TEST_DATA_WITH_TEMPLATE['contact_info']['company']}")
    
    try:
        response = requests.post(endpoint, json=STUDENT_TEST_DATA_WITH_TEMPLATE)
        response.raise_for_status()
        result = response.json()
        
        print("\n=== Student Endpoint with Template Response ===")
        print(f"Status Code: {response.status_code}")
        print(f"Email Draft: {result.get('email_draft', 'No draft generated')[:200]}...")
        print(f"Email Sent: {result.get('email_sent', False)}")
        if not result.get('email_sent', False) and result.get('email_error'):
            print(f"Email Error: {result.get('email_error')}")
        print("=" * 50)
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error testing student endpoint with template: {str(e)}")
        return None

def test_b2b_sales_endpoint_with_template():
    """Test the /generate-email/b2bsales endpoint with a custom template."""
    endpoint = f"{BASE_URL}/generate-email/b2bsales"
    
    print(f"Testing B2B sales endpoint with template: {endpoint}")
    print("Sending request with custom template")
    print(f"User: {B2B_SALES_TEST_DATA_WITH_TEMPLATE['user_info']['name']}")
    print(f"Contact: {B2B_SALES_TEST_DATA_WITH_TEMPLATE['contact_info']['name']} at {B2B_SALES_TEST_DATA_WITH_TEMPLATE['contact_info']['company']}")
    
    try:
        response = requests.post(endpoint, json=B2B_SALES_TEST_DATA_WITH_TEMPLATE)
        
        print("\n=== B2B Sales Endpoint with Template Response ===")
        print(f"Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response Content: {result}")
            
            if response.status_code == 200:
                print(f"Email Draft: {result.get('email_draft', 'No draft generated')[:200]}...")
                print(f"Email Sent: {result.get('email_sent', False)}")
                if not result.get('email_sent', False) and result.get('email_error'):
                    print(f"Email Error: {result.get('email_error')}")
            
            return result
        except Exception as json_err:
            print(f"Error parsing response as JSON: {str(json_err)}")
            print(f"Raw Response: {response.text[:500]}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {str(e)}")
        return None
    finally:
        print("=" * 50)

def main():
    """Run tests based on command line arguments."""
    parser = argparse.ArgumentParser(description='Test Email Manager API endpoints')
    parser.add_argument('--endpoint', choices=['student', 'b2b', 'student-template', 'b2b-template', 'all'], default='all',
                        help='Which endpoint to test (student, b2b, student-template, b2b-template, or all)')
    
    args = parser.parse_args()
    
    if args.endpoint in ['student', 'all']:
        test_student_endpoint()
    
    if args.endpoint in ['b2b', 'all']:
        test_b2b_sales_endpoint()
        
    if args.endpoint in ['student-template', 'all']:
        test_student_endpoint_with_template()
        
    if args.endpoint in ['b2b-template', 'all']:
        test_b2b_sales_endpoint_with_template()

if __name__ == "__main__":
    main()
