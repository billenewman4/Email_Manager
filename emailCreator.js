import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { getSecret } from './secrets.js';

// Convert `import.meta.url` to `__dirname` equivalent
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Function to read example emails from a file
function loadExampleEmails(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

// Function to call GPT-4 API
async function callGPT4(contact, exampleEmails) {
    console.log("Fetching OpenAI API Key...");
    const openai = new OpenAI({
            apiKey: await getSecret('OpenAPI_KEY')
    })
    console.log(contact);
  const { name, email, company, role, linkedInURL, status, nextSteps } = contact;
  var userMessage = '';
    if (status === '1st message sent') {
        userMessage = `
        Here are some example emails:
        ${exampleEmails['first']}

        Write a follow-up email to ${name} at ${company}. 
        - Role: ${role}
        - Email: ${email}
        - LinkedIn: ${linkedInURL}
        - Status: ${status}
        - Next Steps: ${nextSteps}
        
        The email should be professional and courteous while being pithy and powerful. 
    `;

    }else if((status === 'No Contact Yet')) { 

        userMessage = `
        Here are some example emails:
        ${exampleEmails['follow_up']}

        Write a follow-up email to ${name} at ${company}. 
        - Role: ${role}
        - Email: ${email}
        - LinkedIn: ${linkedInURL}
        - Status: ${status}
        - Next Steps: ${nextSteps}
        
        The email should be professional and courteous while being pithy and powerful. 
    `;
    }else{
        console.log("Status is not 1st message sent or No Contact Yet");
        console.log("Status is: ", status);
        userMessage = `
        Write a email to ${name} at ${company}. 
        - Role: ${role}
        - Email: ${email}
        - LinkedIn: ${linkedInURL}
        - Status: ${status}
        - Next Steps: ${nextSteps}

        Here are some example emails:
        ${exampleEmails['first']}
        
        The email should be professional and courteous while being pithy and powerful. 
        `;
    }
  

  const completion = await openai.chat.completions.create({
    messages: [
      { role: 'system', content: 'You are an assistant whose job it is to draft email messages for you boss to use to network with professionals. These emails are essential to his career' },
      { role: 'user', content: userMessage }
    ],
    model: 'gpt-4o-mini',
  });

  return completion.choices[0].message.content; // Adjust based on the actual response structure
}

// Function to generate draft emails for a list of contacts
async function generateDraftEmails(contacts) {
  var exampleEmails = {};
  exampleEmails['first'] = loadExampleEmails(path.join(__dirname, '/email_examples/firstEmails.txt'));
  exampleEmails['follow_up'] = loadExampleEmails(path.join(__dirname, '/email_examples/follow_up_Emails.txt'));
  const draftEmails = [];
  for (const contact of contacts) {
    try {
      console.log(`Generating draft email for ${contact.name}...`);
      const draftEmail = await callGPT4(contact, exampleEmails);
      draftEmails.push({
        contact,
        draftEmail,
      });
    } catch (error) {
      console.error(`Failed to generate draft email for ${contact.name}:`, error);
    }
  }
  console.log(draftEmails)
  return draftEmails;
}

export { generateDraftEmails };