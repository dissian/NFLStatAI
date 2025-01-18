async function uploadDocument() {
    const fileInput = document.getElementById('documentUpload');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/chat/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        alert('Document uploaded successfully!');
    } catch (error) {
        console.error('Error:', error);
        alert('Error uploading document');
    }
}

async function sendQuery() {
    const queryInput = document.getElementById('queryInput');
    const query = queryInput.value.trim();
    if (!query) return;

    try {
        // Show user message immediately
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.innerHTML += `
            <div class="message user">${query}</div>
        `;

        const response = await fetch('/api/chat/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Add bot response
        chatContainer.innerHTML += `
            <div class="message bot">${result.response}</div>
        `;
        
        // Clear input and scroll to bottom
        queryInput.value = '';
        chatContainer.scrollTop = chatContainer.scrollHeight;
    } catch (error) {
        console.error('Error:', error);
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.innerHTML += `
            <div class="message error">Error: Could not get response from server</div>
        `;
    }
}

// Add event listener for Enter key
document.getElementById('queryInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendQuery();
    }
}); 