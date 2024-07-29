import { filterContacts } from './email_todos.js';
import { queryDatabase } from './notion_table.js';
// Importing the function from notion_table.js

// global variables
const statusDaysMap = {
    'Call Scheduled': -1,        // Example: follow-up in 7 days
    'Follow-up Sent': 40,        // Example: follow-up in 14 days
    '1st Message Sent': 10,      // Example: follow-up in 10 days
    'Sent LinkedIn Request': 5,  // Example: follow-up in 5 days
    'No Contact Yet': 1,         // Example: follow-up in 30 days
    'Closed': 50                 // Example: no follow-up needed = -1
};


// Main function to run the process
const main = async () => {
    try {
        const contacts = await queryDatabase(); // Await the Promise to get the resolved contacts array
        console.log("got contacts", contacts);
        const filteredContacts = filterContacts(contacts, statusDaysMap); // Process the resolved contacts
        console.log("Filtered Contacts:", filteredContacts);
    } catch (error) {
        console.error("Error in main function:", error);
    }
};

// Execute the main function
main();