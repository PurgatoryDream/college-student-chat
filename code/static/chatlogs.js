function loadConversations() {
    fetch('/conversations')
        .then(response => response.json())
        .then(data => {
            const conversationsList = document.getElementById('conversations_list');
            conversationsList.innerHTML = '';

            data.conversations.forEach(conversation => {
                const listItem = document.createElement('div');
                listItem.className = 'conversation-list-item';

                listItem.innerText = conversation;  // modify this as necessary
                listItem.addEventListener('click', () => loadConversation(conversation));

                conversationsList.appendChild(listItem);
            });
        });
}

window.addEventListener('load', loadConversations);


function loadConversation(conversation) {
    // Fetch the conversation data from the server
    fetch(`/conversations/${conversation}`)
        .then(response => response.json())
        .then(data => {
            // Clear the chat output
            data = data["log"];
            console.log(data);
            const chatOutput = document.getElementById('chat_output');
            chatOutput.innerHTML = '';

            // Parse the conversation data into messages
            previousClass = "message outgoing";
            const messages = data.split(/(?=Q: |A: )/).map(line => {
                const message = document.createElement('div');
                let previousClass = message.className;
            
                message.className = line.startsWith('A: ') ? 'message incoming' : line.startsWith('Q: ') ? 'message outgoing' : previousClass;
                previousClass = message.className;
            
                message.innerText = line.slice(3);
                return message;
            });

            // Add the messages to the chat output
            messages.forEach(message => chatOutput.appendChild(message));
        });
}
