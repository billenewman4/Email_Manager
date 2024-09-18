// Import node-fetch and dotenv
import fetch from 'node-fetch';
import dotenv from 'dotenv';
import Contact from './contacts.js';
import { getSecret } from './secrets.js';


// Load environment variables from .env file
dotenv.config();


// Function to query database entries
const queryDatabase = async () => {
  const DATABASE_ID = await getSecret('DATABASE_ID');
  console.log("DATABASE_ID:", DATABASE_ID);
  const NOTION_TOKEN = await getSecret('NOTION_TOKEN');
  const url = `https://api.notion.com/v1/databases/${DATABASE_ID}/query`;
  const options = {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${NOTION_TOKEN}`,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
    })
  };

  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      console.log(response);
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    //console.log("Database query result:", data);
    const contacts = processPages(data.results);
    //console.log(`Retrieved ${contacts.length} contacts.`);
    //console.log("Contacts array:", contacts);
    contacts.forEach(contact => contact.printProperties());
    return contacts;
  } catch (error) {
    console.error("Error querying database:", error);
    throw error; // rethrow the error to ensure the calling function is aware of it
  }
};

// Function to process and return an array of Contact instances
const processPages = (pages) => {
  return pages.map(pageData => new Contact(pageData));
};

// Export the queryDatabase function
export { queryDatabase };