// Drag-and-drop
let dropZone = document.getElementById('drop_zone');

dropZone.addEventListener('dragenter', function() {
    dropZone.classList.add('active');
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
});

dropZone.addEventListener('dragleave', function() {
    dropZone.classList.remove('active');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('active');
    let files = e.dataTransfer.files;
    handleFiles(files);
    alert('Document uploaded successfully!');
})

function handleFiles(files) {
    for (let i = 0; i < files.length; i++) {
        // Use the files[i]
        uploadFile(files[i]);
    }
}

// Uploading file to server
function uploadFile(file) {
    let url = '/upload';
    let formData = new FormData();

    formData.append('file', file);

    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(() => { /* Placeholder */ })
    .catch(() => { /* Placeholder */ });
}

// Chat functionality
let chatInput = document.getElementById('chat_input');
let sendButton = document.getElementById('send_button');
let chatContent = document.getElementById('chat_output');

// Giving classes to every message so that they appear differently.
function createMessageElement(text, outgoing) {
    var messageElement = document.createElement('div');
    messageElement.classList.add('message');
    if (outgoing) {
        messageElement.classList.add('outgoing');
    } else {
        messageElement.classList.add('incoming');
    }
    messageElement.textContent = text;
    return messageElement;
}

sendButton.addEventListener('click', () => {
    let message = chatInput.value;
    chatInput.value = '';

    // Append the question to the chat
    var messageElement = createMessageElement(message, true);
    chatContent.append(messageElement);

    // Send the question to the server
    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: message })
    })
    .then(response => response.json())
    .then(data => {
        // Append the server's answer to the chat
        let answerElement = createMessageElement(data.answer, false);
        chatContent.append(answerElement);
    });
});

// To obtain the documents
fetch('/documents', {
    method: 'GET',
    credentials: 'same-origin' // Include cookies
})
.then(response => response.json())
.then(data => {
    let fileSelect = document.getElementById('file_select');
    for(let file of data.files) {
        let option = document.createElement('option');
        option.value = file;
        option.text = file;
        fileSelect.appendChild(option);
    }
})
.catch(() => { /* Handle error */ });

// Add an event listener to the open file button:
let openFileButton = document.getElementById('open_file_button');
openFileButton.addEventListener('click', function() {
    let fileSelect = document.getElementById('file_select');
    let selectedFile = fileSelect.options[fileSelect.selectedIndex].value;
    window.open('/uploads/' + encodeURIComponent(selectedFile));
});

// Add an event listener to the delete file button:
let deleteButton = document.getElementById('delete_file_button');
deleteButton.addEventListener('click', function() {
    let fileSelect = document.getElementById('file_select');
    if (fileSelect.selectedIndex >= 0) {
        let filename = fileSelect.options[fileSelect.selectedIndex].value;
        
        fetch('/delete-file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({filename: filename}),
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            } else {
                alert('File deleted successfully!');
                fileSelect.remove(fileSelect.selectedIndex);
            }
        })
        .catch((error) => {
            console.error('There was a problem with the fetch operation:', error);
        });
    } else {
        alert('Please select a file to delete.');
    }
});