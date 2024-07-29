import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Convert `import.meta.url` to `__dirname` equivalent
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const openai = new OpenAI({
        apiKey: process.env.OpenAPI_KEY,
});

// Function to read example emails from a file
function loadExampleEmails(filePath) {
    return fs.readFileSync(filePath, 'utf8');
}

// Function to call GPT-4 API
async function callGPT4(contact, exampleEmails) {
  const { name, email, company, role, linkedInURL, status, nextSteps } = contact;

  const userMessage = `
    Here are some example emails:
    ${exampleEmails}

    Write a follow-up email to ${name} at ${company}. 
    - Role: ${role}
    - Email: ${email}
    - LinkedIn: ${linkedInURL}
    - Status: ${status}
    - Next Steps: ${nextSteps}
    
    The email should be professional and courteous while being pithy and powerful. 
  `;

  const completion = await openai.chat.completions.create({
    messages: [
      { role: 'system', content: 'You are an assistant whose job it is to draft email messages for you boss to use to network with professionals. These emails are essiental to his career' },
      { role: 'user', content: userMessage }
    ],
    model: 'gpt-4o-mini',
  });

  return completion.choices[0].message.content; // Adjust based on the actual response structure
}

// Function to generate draft emails for a list of contacts
async function generateDraftEmails(contacts) {
  const exampleEmails = loadExampleEmails(path.join(__dirname, 'emailExamples.txt'));
  const draftEmails = [];

  for (const contact of contacts) {
    try {
      const draftEmail = await callGPT4(contact, exampleEmails);
      draftEmails.push({
        contact,
        draftEmail,
      });
    } catch (error) {
      console.error(`Failed to generate draft email for ${contact.name}:`, error);
    }
  }

  return draftEmails;
}

export { generateDraftEmails };