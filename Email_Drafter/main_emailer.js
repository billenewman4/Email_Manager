import express from 'express';
import nodemailer from 'nodemailer';
import { getSecret } from './secrets.js';
import cors from 'cors';

const app = express();
app.use(express.json());
app.use(cors({
    origin: ["http://localhost:5000", "http://localhost:8002"],  // Allow both Flask and FastAPI
    methods: ["POST"],
}));

// Email sending function
async function sendDraftEmail(recipientEmail, emailDraft) {
    try {
        console.log("Sending email to:", recipientEmail);
        const EMAIL_USER = await getSecret("EMAIL_USER");
        const EMAIL_PASS = await getSecret("EMAIL_PASS");

        const transporter = nodemailer.createTransport({
            service: 'gmail',
            auth: {
                user: EMAIL_USER,
                pass: EMAIL_PASS,
            },
        });

        const mailOptions = {
            from: EMAIL_USER,
            to: recipientEmail,
            subject: "Networking Connection",
            text: emailDraft,
        };

        await transporter.sendMail(mailOptions);
        console.log(`Email sent successfully to ${recipientEmail}`);
        return {
            success: true,
            message: "Email sent successfully"
        };
    } catch (error) {
        console.error(`Failed to send email to ${recipientEmail}:`, error);
        return {
            success: false,
            message: error.message
        };
    }
}

// Email service endpoint
app.post('/send-email', async (req, res) => {
    console.log("Received email request:", req.body);
    
    const { recipientEmail, emailDraft } = req.body;
    
    if (!recipientEmail || !emailDraft) {
        return res.status(400).json({
            success: false,
            message: "Recipient email and draft are required"
        });
    }

    try {
        const result = await sendDraftEmail(recipientEmail, emailDraft);
        res.json(result);
    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});

// Start the server
const PORT = 8003;
app.listen(PORT, () => {
    console.log(`Email service running on port ${PORT}`);
});