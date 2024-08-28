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

const uploadButton = document.getElementById('upload-button');
const pdfInput = document.getElementById('pdf-input');
const pdfForm = document.getElementById('pdf-form');
const spinner = document.getElementById('spinner');

uploadButton.addEventListener('click', () => {
    if (uploadButton.textContent.trim() === 'Upload File') {
        pdfInput.click();
    } else if (uploadButton.textContent.trim() === 'Send') {
        processFile();
    } else if (uploadButton.textContent.trim() === 'Download') {
        downloadSummary();
    }
});

pdfInput.addEventListener('change', () => {
    if (pdfInput.files.length > 0) {
        uploadButton.querySelector('span').textContent = 'Send';
    }
});

function processFile() {
    const formData = new FormData(pdfForm);
    const file = pdfInput.files[0];
    formData.append('file_path', file);

    const fileExtension = file.name.split('.').pop().toLowerCase();
    let route = '';

    if (fileExtension === 'pdf') {
        route = '/process_pdf';
    } else if (fileExtension === 'ipynb') {
        route = '/process_ipynb';
    } else {
        alert('Unsupported file format.');
        return;
    }

    // Показываем спиннер и скрываем кнопку отправки
    spinner.style.display = 'block';
    uploadButton.querySelector('span').textContent = 'Processing...';
    uploadButton.disabled = true; // Отключаем кнопку

    fetch(route, {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        document.getElementById('chat-box').innerHTML += `<div class="chatbox__messages__user-message--ind-message bot-message"><p class="name">Bot:</p><p class="message">${data}</p></div>`;
        uploadButton.querySelector('span').textContent = 'Download';
    })
    .catch(error => console.error('Error:', error))
    .finally(() => {
        // Скрываем спиннер и активируем кнопку
        spinner.style.display = 'none';
        uploadButton.disabled = false;
    });
}

function downloadSummary() {
    window.location.href = '/download_summary';
}
