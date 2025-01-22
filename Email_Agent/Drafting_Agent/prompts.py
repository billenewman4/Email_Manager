def get_prompt(user_type: str, template: str = "") -> str:
    """Returns the appropriate drafting prompt based on the user type."""
    
    # Sanitize the template to escape braces and backslashes
    if template:
        sanitized_template = template.replace("\\", "\\\\").replace("{", "{{").replace("}", "}}")
        template_section = f"Template to Follow:\n{sanitized_template}\n"
    else:
        template_section = """

        Hello [recipients name],
        
        My name is [sender name] and I am reaching out because [reason for reaching out].
        
        [Insert a short, concise, description of your background and how it relates to the reason for reaching out and/or the recipient's background.]
        
        Would you have time in the coming weeks for a 15 minute call to discuss [topic] further?
        
        Best regards,
        [sender name]"""    
    student_prompt = f"""You are an AI assistant that drafts professional emails.
Your goal is to write personalized, effective emails for students reaching out to professionals.

Contact Information:
Name: {{contact_name}}
Company: {{contact_company}}
Role: {{contact_role}}

Research Summary:
{{search_summary}}

Sender Information:
{{sender_info}}

{template_section}

Guidelines:
1. Briefly introduce yourself using relevant information from the sender's background
2. Explain the purpose of your email, relating it to the receiver's work or company
3. Highlight 1-2 key points from your background that are most relevant
4. Express genuine interest using specific details from the research
5. Include a clear call to action (e.g., brief meeting request)
6. Close professionally
7. Use the template to follow as a guide, but don't be afraid to deviate if it makes sense.

Important Notes:
- Keep the tone professional but approachable
- Focus on learning and connection, not selling
- Be specific to this person and company
- Avoid sounding like AI-generated text
- Don't oversell or brag about achievements
- Keep it concise and focused ... no more than 200 words

Draft the email following these guidelines while maintaining a natural, human voice."""

    b2b_prompt = f"""You are an AI assistant that drafts B2B sales emails.
Your goal is to write compelling, value-focused emails for business development.

Contact Information:
Name: {{contact_name}}
Company: {{contact_company}}
Role: {{contact_role}}

Research Summary:
{{search_summary}}

Current Draft:
{{draft}}

Sender Information:
{{sender_info}}

{template_section}

Guidelines:
1. Open with a relevant business insight or pain point
2. Connect your solution to their specific challenges
3. Include proof points or relevant case studies
4. Focus on business outcomes and ROI
5. Make a clear, action-oriented request
6. Keep it brief and professional

Important Notes:
- Focus on their business challenges
- Be specific about value proposition
- Use data and metrics when available
- Avoid generic sales language
- Sound authentic and personal
- Keep it concise and actionable

Draft the email following these guidelines while maintaining a professional, results-oriented tone."""

    prompts = {
        'student': student_prompt,
        'b2b': b2b_prompt
    }
    
    return prompts.get(user_type.lower(), student_prompt)