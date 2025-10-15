const API_BASE = 'http://localhost:8000/api/v1';
const WORKSPACE_ID = 'default';

let uploadedFiles = [];
let conversationId = null;

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    if (tabName === 'documents') {
        loadDocuments();
    }
}

// File upload handling
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');

uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

async function handleFiles(files) {
    for (const file of files) {
        await uploadFile(file);
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/upload?workspace_id=${WORKSPACE_ID}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        uploadedFiles.push(data);
        displayFile(data);
        
        // Trigger indexing
        await indexDocument(data.document_id);
        
    } catch (error) {
        console.error('Upload failed:', error);
        alert('Upload failed: ' + error.message);
    }
}

async function indexDocument(documentId) {
    try {
        await fetch(`${API_BASE}/index/${documentId}?workspace_id=${WORKSPACE_ID}`, {
            method: 'POST'
        });
        
        // Poll for status
        checkStatus(documentId);
        
    } catch (error) {
        console.error('Indexing failed:', error);
    }
}

async function checkStatus(documentId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/status/${documentId}`);
            const data = await response.json();
            
            updateFileStatus(documentId, data.status);
            
            if (data.status === 'completed' || data.status === 'failed') {
                clearInterval(interval);
            }
        } catch (error) {
            clearInterval(interval);
        }
    }, 2000);
}

function displayFile(fileData) {
    const fileList = document.getElementById('fileList');
    
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.id = `file-${fileData.document_id}`;
    
    fileItem.innerHTML = `
        <div class="file-info">
            <div class="file-name">${fileData.filename}</div>
            <div class="file-status status-${fileData.status}">${fileData.status}</div>
        </div>
        <button onclick="deleteDocument('${fileData.document_id}')">Delete</button>
    `;
    
    fileList.appendChild(fileItem);
}

function updateFileStatus(documentId, status) {
    const fileItem = document.getElementById(`file-${documentId}`);
    if (fileItem) {
        const statusEl = fileItem.querySelector('.file-status');
        statusEl.textContent = status;
        statusEl.className = `file-status status-${status}`;
    }
}

// Chat functionality
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Display user message
    addMessage(message, 'user');
    input.value = '';
    
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                workspace_id: WORKSPACE_ID,
                conversation_id: conversationId
            })
        });
        
        const data = await response.json();
        
        conversationId = data.conversation_id;
        
        // Display assistant message
        addMessage(data.response, 'assistant', data.sources);
        
    } catch (error) {
        console.error('Chat failed:', error);
        addMessage('Sorry, something went wrong.', 'assistant');
    }
}

function addMessage(text, role, sources = null) {
    const messagesDiv = document.getElementById('messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.textContent = text;
    
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'sources';
        sourcesDiv.innerHTML = '<strong>Sources:</strong>';
        
        sources.forEach((source, i) => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            sourceItem.textContent = `[${i + 1}] ${source.content.substring(0, 100)}...`;
            sourcesDiv.appendChild(sourceItem);
        });
        
        messageDiv.appendChild(sourcesDiv);
    }
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Enter key to send
document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Load documents list
async function loadDocuments() {
    const documentsList = document.getElementById('documentsList');
    documentsList.innerHTML = '<p>Loading documents...</p>';
    
    // This would call a GET /documents endpoint
    // For now, show uploaded files
    documentsList.innerHTML = '';
    
    uploadedFiles.forEach(file => {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
            <div class="file-info">
                <div class="file-name">${file.filename}</div>
                <div class="file-status">${file.file_type} • ${(file.size / 1024).toFixed(2)} KB</div>
            </div>
        `;
        documentsList.appendChild(item);
    });
}