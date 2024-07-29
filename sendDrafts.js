import nodemailer from 'nodemailer';

// Function to send an email
async function sendEmail(to, subject, text) {
  // Create a transporter object using the default SMTP transport
  const transporter = nodemailer.createTransport({
    service: 'gmail', // Use your email service provider
    auth: {
      user: process.env.EMAIL_USER, // Your email address
      pass: process.env.EMAIL_PASS, // Your email password or app-specific password
    },
  });

  // Set up email data
  const mailOptions = {
    from: process.env.EMAIL_USER, // Sender address
    to: to, // List of receivers
    subject: subject, // Subject line
    text: text, // Plain text body
  };

  // Send mail with defined transport object
  await transporter.sendMail(mailOptions);
}

// Function to send all draft emails
async function sendDraftEmails(draftEmails) {
  const emailAddress = process.env.MY_EMAIL; // Your email address to receive the drafts
  for (const { contact, draftEmail } of draftEmails) {
    const subject = `Draft email for ${contact.name}`;
    const text = draftEmail;
    try {
      await sendEmail(emailAddress, subject, text);
      console.log(`Email sent for ${contact.name}`);
    } catch (error) {
      console.error(`Failed to send email for ${contact.name}:`, error);
    }
  }
}

export { sendDraftEmails };