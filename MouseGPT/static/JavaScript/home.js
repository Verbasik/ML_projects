const socket = io.connect();

document.getElementById('send-button').addEventListener('click', () => {
    const userInput = document.getElementById('user-input').value;
    if (userInput) {
        appendMessage('You', userInput, 'user-message');
        socket.emit('message', { message: userInput });
        document.getElementById('user-input').value = '';
    }
});

socket.on('response', (data) => {
    appendMessage('Nia', data.message, 'bot-message');
});

function appendMessage(sender, message, className) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.className = `chatbox__messages__user-message--ind-message ${className}`;
    messageElement.innerHTML = `<p class="name">${sender}:</p><p class="message">${message}</p>`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

const uploadButton = document.getElementById('upload-button');
const pdfInput = document.getElementById('pdf-input');
const pdfForm = document.getElementById('pdf-form');

uploadButton.addEventListener('click', () => {
    if (uploadButton.textContent.trim() === 'Upload PDF') {
        pdfInput.click();
    } else if (uploadButton.textContent.trim() === 'Send') {
        processPDF();
    } else if (uploadButton.textContent.trim() === 'Download') {
        downloadSummary();
    }
});

pdfInput.addEventListener('change', () => {
    if (pdfInput.files.length > 0) {
        uploadButton.querySelector('span').textContent = 'Send';
    }
});

function processPDF() {
    const formData = new FormData(pdfForm);
    formData.append('file_path', pdfInput.files[0]);

    fetch('/process_pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        document.getElementById('chat-box').innerHTML += `<div class="chatbox__messages__user-message--ind-message bot-message"><p class="name">Bot:</p><p class="message">${data}</p></div>`;
        uploadButton.querySelector('span').textContent = 'Download';
    })
    .catch(error => console.error('Error:', error));
}

function downloadSummary() {
    window.location.href = '/download_summary';
}
