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
      console.log('---------------------------------------------------');
    }
    /**
 * Function to filter contacts based on the last contact date and status.
 * @param {Contact[]} contacts - An array of Contact instances.
 * @returns {string[]} - An array of names of contacts who meet the criteria.
 */
    isReachOutNeeded(statusDaysArray) {
        const daysToNextContact = statusDaysArray[this.status];
        if (daysToNextContact === undefined) {
            return false;
        }    
        const lastContactedDate = this.dateLastContacted ? parseISO(this.dateLastContacted) : null;

        if (!lastContactedDate) {
            return false;
        }
    
        const daysSinceContact = differenceInDays(new Date(), lastContactedDate);
        return daysToNextContact != -1 && daysSinceContact >= daysToNextContact;
      }
  }
  
  export default Contact;