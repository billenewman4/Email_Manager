import express from 'express';
import { filterContacts } from './filter_contacts.js';
import { queryDatabase } from './notion_table.js';
import { generateDraftEmails } from './emailCreator.js';
import { sendDraftEmails } from './sendDrafts.js';

const app = express();
const port = process.env.PORT || 8080;

// URL of the web_scrapper service
const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'https://python-scraper-usaz4344ba-wl.a.run.app';

// global variables
const statusDaysMap = {
    'Call Scheduled': -1,        // Example: follow-up in 7 days
    'Follow-up Sent': -1,        // Example: follow-up in 14 days
    '1st Message Sent': 10,      // Example: follow-up in 10 days
    'Sent LinkedIn Request': -1,  // Example: follow-up in 5 days
    'No Contact Yet': 1,         // Example: follow-up in 30 days
    'Closed': -1,                // Example: follow-up in 50 days
    'No need for follow-up': -1  // Example: no follow-up needed = -1
};

async function callPythonScraper(query) {
    try {
        const response = await axios.post(`${PYTHON_SERVICE_URL}/scrape`, { query });
        return response.data;
    } catch (error) {
        console.error('Error calling Python scraper:', error);
        throw error;
    }
}

// Endpoint to trigger the main process
app.get('/run', async (req, res) => {
    try {
        console.log("Starting the main process...");
        const contacts = await queryDatabase();
        console.log("Successfully retrieved contacts from the database.");
        const filteredContacts = filterContacts(contacts, statusDaysMap);
        console.log("Successfully filtered contacts", filteredContacts);

        // Call the Python scraper for each contact (example)
        for (let contact of filteredContacts) {
            if (contact.company && contact.company !== null) {
                const scrapingResult = await callPythonScraper(contact.company);
                contact.setCompanyInfo(scrapingResult);
                console.log("Successfully scraped info for", contact.company);
                console.log("Scraped info:", contact.scrapedInfo);
            }
        }
        const draftEmails = await generateDraftEmails(filteredContacts);
        await sendDraftEmails(draftEmails, filteredContacts);
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