def get_prompt(supervisor_type: str, template: str = "") -> str:
    """Returns the appropriate supervisor prompt based on the type."""
    
    student_prompt = f"""You are a supervisor evaluating an email draft. Your job is to determine if the email needs revision because the wording is bad, needs more research (e.g., like a google search to learn more about the contact), or is ready to send.

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

{f'Template to Follow:\n{template}\n' if template else ''}

Evaluate the email based on these criteria:
1. Does it effectively use the research about the contact?
2. Is the tone appropriate for a student reaching out?
3. Is it personalized and specific enough or could the same email be sent to multiple contacts?
4. Does it have a clear purpose and call to action?
5. Does it avoid common mistakes (being too pushy, too formal, or too casual)?
6. Is the email tailored to the receiver's company and role?
7. Is the email tailored to the sender's background and interests?
8. Is the email over wordy?
9. Does the email sound like it was written by chatGPT?

Response options are:
REDRAFT: The email needs revision because the wording is bad, needs more research, or is not personalized enough.
SEARCH: The email needs more research because the contact information is not specific enough.
END: The email is ready to send.

Please be a tough critic.

Respond in the following format:
COMMAND: [REDRAFT/SEARCH/END]
REASON: [Brief explanation of your decision]
DETAILS: [If REDRAFT - specific critiques and suggestions, If SEARCH - specific information to look for, If END - brief confirmation of why email is ready]"""

    b2b_prompt = f"""You are a supervisor evaluating a B2B sales email draft. Your job is to determine if the email needs revision, requires additional research about the prospect, or is ready to send.

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

{f'Template to Follow:\n{template}\n' if template else ''}

Evaluate the email based on these criteria:
1. Does it effectively leverage the research about the prospect's pain points?
2. Is the tone appropriate for a B2B sales context?
3. Is it personalized to the prospect's specific business challenges?
4. Does it have a clear value proposition and call to action?
5. Does it avoid common sales email mistakes (being too pushy, too generic, or too feature-focused)?
6. Is the email focused on business outcomes and ROI?
7. Does it establish credibility through relevant case studies or metrics?
8. Is the email concise and focused?
9. Does it sound authentic and not overly automated?

Response options are:
REDRAFT: The email needs revision due to messaging, value proposition, or personalization issues.
SEARCH: More research needed about prospect's business challenges or recent developments.
END: The email is ready to send.

Please evaluate with a focus on sales effectiveness.

Respond in the following format:
COMMAND: [REDRAFT/SEARCH/END]
REASON: [Brief explanation of your decision]
DETAILS: [If REDRAFT - specific sales messaging improvements, If SEARCH - specific business intelligence needed, If END - confirmation of sales readiness]"""

    prompts = {
        'student': student_prompt,
        'b2b': b2b_prompt
    }
    
    return prompts.get(supervisor_type.lower(), student_prompt)