// static/JavaScript/home.js
const socket = io.connect({
    transports: ['websocket', 'polling']
});

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

const uploadFileButton = document.getElementById('upload-file-button');
const fileInput = document.getElementById('file-input');
const fileForm = document.getElementById('file-form');
const spinner = document.getElementById('spinner');

uploadFileButton.addEventListener('click', () => {
    if (uploadFileButton.textContent.trim() === 'Upload File') {
        fileInput.click();
    } else if (uploadFileButton.textContent.trim() === 'Send') {
        processFile();
    } else if (uploadFileButton.textContent.trim() === 'Download') {
        downloadSummary();
    }
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        uploadFileButton.querySelector('span').textContent = 'Send';
    }
});

function processFile() {
    const formData = new FormData(fileForm);
    const file = fileInput.files[0];
    formData.append('file_path', file);

    const fileExtension = file.name.split('.').pop().toLowerCase();
    let route = '';

    // Определение маршрута в зависимости от типа файла
    if (fileExtension === 'pdf') {
        route = '/process_pdf';
    } else if (fileExtension === 'ipynb') {
        route = '/process_ipynb';
    } else if (['mp4', 'mov', 'avi', 'm4a'].includes(fileExtension)) {
        route = '/process_video';
    } else if (['mp3', 'wav', 'ogg'].includes(fileExtension)) {
        route = '/process_audio';
    } else {
        alert('Unsupported file format.');
        return;
    }

    spinner.style.display = 'block';
    uploadFileButton.querySelector('span').textContent = 'Processing...';
    uploadFileButton.disabled = true;

    fetch(route, {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        document.getElementById('chat-box').innerHTML += `<div class="chatbox__messages__user-message--ind-message bot-message"><p class="name">Bot:</p><p class="message">${data}</p></div>`;
        uploadFileButton.querySelector('span').textContent = 'Download';
    })
    .catch(error => console.error('Error:', error))
    .finally(() => {
        spinner.style.display = 'none';
        uploadFileButton.disabled = false;
    });
}

function downloadSummary() {
    window.location.href = '/download_summary';
}
