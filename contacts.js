import { differenceInDays, parseISO } from 'date-fns';

class Contact {
    constructor(pageData) {
      this.id = pageData.id;
      this.name = pageData.properties['Name of the Contact']?.title?.map(textObj => textObj.plain_text).join(' ') || null;
      this.createdTime = pageData.created_time;
      this.lastEditedTime = pageData.last_edited_time;
      this.url = pageData.url;
      this.email = pageData.properties.Email?.email || null;
      this.linkedInURL = pageData.properties['LinkedIn URL']?.url || null;
      this.dateLastContacted = pageData.properties['Date Last Contacted']?.date?.start || null;
      this.status = pageData.properties.Status?.select?.name || null;
      this.nextSteps = pageData.properties['Next Steps']?.rich_text?.map(textObj => textObj.plain_text).join(' ') || null;
      this.role = pageData.properties.Role?.rich_text?.map(textObj => textObj.plain_text).join(' ') || null;
      this.contactType = pageData.properties['Contact Type']?.select?.name || null;
      this.meetingNotes = pageData.properties['Meeting notes/other']?.rich_text?.map(textObj => textObj.plain_text).join(' ') || null;
      this.company = pageData.properties.Company?.rich_text?.map(textObj => textObj.plain_text).join(' ') || null;
    }
  
    printProperties() {
      console.log(`Page ID: ${this.id}`);
      console.log(`Name: ${this.name}`);
      console.log(`Created Time: ${this.createdTime}`);
      console.log(`Last Edited Time: ${this.lastEditedTime}`);
      console.log(`URL: ${this.url}`);
      console.log(`Email: ${this.email}`);
      console.log(`LinkedIn URL: ${this.linkedInURL}`);
      console.log(`Date Last Contacted: ${this.dateLastContacted}`);
      console.log(`Status: ${this.status}`);
      console.log(`Next Steps: ${this.nextSteps}`);
      console.log(`Role: ${this.role}`);
      console.log(`Contact Type: ${this.contactType}`);
      console.log(`Meeting Notes: ${this.meetingNotes}`);
      console.log(`Company: ${this.company}`);
      console.log('---------------------------------------------------');
    }
    /**
 * Function to filter contacts based on the last contact date and status.
 * @param {Contact[]} contacts - An array of Contact instances.
 * @returns {string[]} - An array of names of contacts who meet the criteria.
 */
    isReachOutNeeded(statusDaysArray) {
      // Handle the case where the status is not found in the array
      const daysToNextContact = statusDaysArray[this.status];
      if (daysToNextContact === undefined) {
          console.log(`Status "${this.status}" not found in statusDaysArray, skipping ${this.name}`);
          return false;
      }

      // If the status indicates no follow-up is needed, return false immediately
      if (daysToNextContact === -1) {
          return false;
      }
      
      // Handle missing or invalid last contacted date
      if (!this.dateLastContacted) {
          console.log(`No last contacted date for ${this.name}, considering for follow-up.`);
          return true; // Consider as needing follow-up if no date is provided
      }

      let lastContactedDate;
      try {
          lastContactedDate = parseISO(this.dateLastContacted);
      } catch (error) {
          console.error(`Error parsing date for ${this.name}: ${error}`);
          return false; // Exclude if date parsing fails
      }

      const daysSinceContact = differenceInDays(new Date(), lastContactedDate);

      // Consider if it's time to reach out again
      if (daysSinceContact >= daysToNextContact) {
          return true;
      } else {
          console.log(`${this.name} was contacted ${daysSinceContact} days ago. No follow-up needed yet.`);
          return false;
      }
    }
  }
  
  export default Contact;