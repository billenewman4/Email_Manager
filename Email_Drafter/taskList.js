

async function taskList(contacts){
    var taskList = [];
    for (const contact of contacts){
        taskList.push({
            contact: contact['name'],
            contact: contact['status'],
            contact: contact['dateLastContacted'],
        });
    
    }

}