import express from 'express';
import { filterContacts } from './filter_contacts.js';
import { queryDatabase } from './notion_table.js';
import { generateDraftEmails } from './emailCreator.js';
import { sendDraftEmails } from './sendDrafts.js';

const app = express();
const port = process.env.PORT || 8080;

// global variables
const statusDaysMap = {
    'Call Scheduled': -1,        // Example: follow-up in 7 days
    'Follow-up Sent': 40,        // Example: follow-up in 14 days
    '1st Message Sent': 10,      // Example: follow-up in 10 days
    'Sent LinkedIn Request': 5,  // Example: follow-up in 5 days
    'No Contact Yet': 1,         // Example: follow-up in 30 days
    'Closed': 50,                // Example: follow-up in 50 days
    'No need for follow-up': -1  // Example: no follow-up needed = -1
};

// Endpoint to trigger the main process
app.get('/run', async (req, res) => {
    try {
        console.log("Starting the main process...");
        const contacts = await queryDatabase(); // Await the Promise to get the resolved contacts array
        console.log("Successfully retrieved contacts from the database.");
        const filteredContacts = filterContacts(contacts, statusDaysMap); // Process the resolved contacts
        console.log("Successfully filtered contacts", filteredContacts);
        const draftEmails = await generateDraftEmails(filteredContacts);
        await sendDraftEmails(draftEmails, filteredContacts); // Send all draft emails to yourself
        res.send('Draft emails generated and sent successfully!');
    } catch (error) {
        console.error("Error in main function:", error);
        res.status(500).send('An error occurred while generating and sending draft emails.');
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});