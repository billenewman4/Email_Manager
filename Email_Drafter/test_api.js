import express from 'express';
import axios from 'axios';

const app = express();
const port = 3000;

// Get Flask service URL from environment with new default port
const FLASK_PORT = process.env.FLASK_PORT || 6000;
const FLASK_SERVICE_URL = process.env.FLASK_SERVICE_URL || `http://localhost:${FLASK_PORT}`;

// Configure express to parse JSON
app.use(express.json());

// Test endpoint
app.get('/test-email', async (req, res) => {
    console.log('Received request to /test-email');
    console.log('Attempting to connect to Flask service at:', FLASK_SERVICE_URL);
    
    try {
        // Create test data based on the sample contact
        const testData = {
            contact: {
                id: 'sample-id-123',
                name: 'Monica Varman',
                company: 'G2 Venture Partners',
                role: 'Venture Partner',
                email: 'monica.varman@example.com',
                linkedInURL: null,
                status: '1st Message Sent'
            },
            sender: {
                name: "Bill Newman",
                resume: "Sample resume content...",
                career_interest: "Interested in how Service-as-a-Software (SaaS) companies are using AI to automate business services",
                key_accomplishments: [
                    "Worked at a YC backed startup using AI to increase agricultural productivity, at McKinsey worked for startups in the blockchain, SaaS, and quantum computing sectors",
                    "Currently a student at Harvard Business School (HBS) studying a master in business administration and I am interested in vertical application for AI in enterprise software"
                ]
            }
        };

        console.log('Making request to Flask service with test data');
        
        // Make request to Flask service with timeout
        const response = await axios.post(`${FLASK_SERVICE_URL}/generate-email`, testData, {
            timeout: 30000,  // Increased timeout for production
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 403) {
            console.error('Received 403 Forbidden from Flask service');
            return res.status(403).json({
                status: 'error',
                message: 'Access forbidden to Flask service. Please check server configuration.'
            });
        }

        // Return the results
        console.log('Received successful response from Flask service');
        res.json({
            status: 'success',
            data: response.data
        });

    } catch (error) {
        if (error.code === 'ECONNREFUSED') {
            console.error(`Connection refused to Flask server at ${FLASK_SERVICE_URL}`);
            return res.status(500).json({
                status: 'error',
                message: `Connection refused to Flask server at ${FLASK_SERVICE_URL}`
            });
        }

        console.error('Error details:', {
            message: error.message,
            code: error.code,
            response: error.response ? {
                status: error.response.status,
                data: error.response.data
            } : 'No response data'
        });

        res.status(500).json({
            status: 'error',
            message: error.message,
            details: error.response ? error.response.data : null
        });
    }
});

app.listen(port, () => {
    console.log(`Test server running at http://localhost:${port}`);
    console.log(`Configured to connect to Flask service at: ${FLASK_SERVICE_URL}`);
}); 