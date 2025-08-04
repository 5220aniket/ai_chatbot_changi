document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const status = document.getElementById('status');
    
    // Add message to chat history
    function addMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        
        const header = document.createElement('div');
        header.classList.add('message-header');
        header.textContent = isUser ? 'You' : 'Changi Assistant';
        
        const content = document.createElement('div');
        content.textContent = text;
        
        messageDiv.appendChild(header);
        messageDiv.appendChild(content);
        chatHistory.appendChild(messageDiv);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
    // Send message to API
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message
        addMessage(message, true);
        userInput.value = '';
        
        // Show typing indicator
        status.textContent = "Changi Assistant is thinking...";
        
        try {
            // Send request to API
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `question=${encodeURIComponent(message)}`
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Add bot response
            addMessage(data.answer, false);
            status.textContent = "Ready to assist you!";
        } catch (error) {
            console.error('Error:', error);
            addMessage("Sorry, I'm having trouble answering that right now. Please try again later.", false);
            status.textContent = "Error occurred. Please try again.";
        }
    }
    
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Focus input field on load
    userInput.focus();
});