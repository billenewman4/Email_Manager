/**
 * Function to filter contacts based on the last contact date and status.
 * @param {Contact[]} contacts - An array of Contact instances.
 * @param {Object} statusDaysMap - An object where the key is the status and the value is the days to next contact.
 * @returns {string[]} - An array of names of contacts who meet the criteria.
 */
const filterContacts = (contacts, statusDaysMap) => {
    return contacts
      .filter(contact => contact.isReachOutNeeded(statusDaysMap))
      .map(contact => {
        return {
          name: contact.name,
          email: contact.email,
          status: contact.status,
          role: contact.role,
          company: contact.company,
          meetingNotes: contact.meetingNotes
        }
      });
  };
  
  export { filterContacts };