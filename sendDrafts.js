import nodemailer from 'nodemailer';
import { getSecret } from './secrets.js';

// Function to send an email
async function sendEmail(to, subject, text) {
    const EMAIL_USER = await getSecret("EMAIL_USER");
    const EMAIL_PASS = await getSecret("EMAIL_PASS");

    // Create a transporter object using the default SMTP transport
    const transporter = nodemailer.createTransport({
        service: 'gmail', // Use your email service provider
        auth: {
            user: EMAIL_USER, // Your email address
            pass: EMAIL_PASS, // Your email password or app-specific password
        },
    });

    // Set up email data
    const mailOptions = {
        from: EMAIL_USER, // Sender address
        to: to, // List of receivers
        subject: subject, // Subject line
        text: text, // Plain text body
    };

    // Send mail with defined transport object
    await transporter.sendMail(mailOptions);
}

// Function to send all draft emails in one email
async function sendDraftEmails(draftEmails) {
    const MY_EMAIL = await getSecret("MY_EMAIL");
    const emailAddress = MY_EMAIL; // Your email address to receive the drafts

    // Concatenate all draft emails into a single string
    let emailBody = 'Here are your draft emails:\n\n';
    for (const { contact, draftEmail } of draftEmails) {
        emailBody += `Draft email for ${contact.name} (${contact.email}):\n\n`;
        emailBody += `${draftEmail}\n\n`;
        emailBody += '---------------------------\n\n';
    }

    const subject = 'All Draft Emails';
    try {
        await sendEmail(emailAddress, subject, emailBody);
        console.log(`All draft emails sent successfully.`);
    } catch (error) {
        console.error(`Failed to send draft emails:`, error);
    }
}

export { sendDraftEmails };