
        let ws = null;
        let username = '';
        let currentRoom = 'general';

        function updateConnectionStatus(connected) {
            const status = document.getElementById('connectionStatus');
            if (connected) {
                status.innerHTML = '<span class="online-indicator"></span>Connected to ' + currentRoom;
            } else {
                status.innerHTML = '<span class="offline-indicator"></span>Disconnected';
            }
        }

        function connect() {
            const usernameInput = document.getElementById('usernameInput');
            const roomInput = document.getElementById('roomInput');
            
            username = usernameInput.value.trim();
            currentRoom = roomInput.value.trim() || 'general';
            
            if (!username) {
                alert('Please enter a username');
                return;
            }

            // Create WebSocket connection
            const wsUrl = `ws://localhost:8001/api/ws/${username}?room_id=${currentRoom}`;
            console.log(wsUrl)
            ws = new WebSocket(wsUrl);
           
            ws.onopen = function(event) {
                updateConnectionStatus(true);
                document.getElementById('loginSection').classList.add('hidden');
                document.getElementById('messageForm').classList.remove('hidden');
                addMessage('System', `Connected to room: ${currentRoom}`, 'system');
            };

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                console.log('Received:', data);
                
                const messageType = data.message_type || 'chat';
                const sender = data.username;
                const message = data.message;
                
                addMessage(sender, message, messageType);
            };

            ws.onclose = function(event) {
                updateConnectionStatus(false);
                addMessage('System', 'Disconnected from server', 'system');
                document.getElementById('loginSection').classList.remove('hidden');
                document.getElementById('messageForm').classList.add('hidden');
            };

            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                addMessage('System', 'Connection error occurred', 'system');
            };
        }

        function sendMessage() {
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (!message || !ws || ws.readyState !== WebSocket.OPEN) {
                return;
            }

            const messageData = {
                message: message,
                timestamp: new Date().toISOString()
            };

            ws.send(JSON.stringify(messageData));
            messageInput.value = '';
        }

        function addMessage(sender, message, type = 'chat') {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            
            let messageClass = 'message other';
            if (sender === username) {
                messageClass = 'message own';
            } else if (type === 'system' || type === 'user_join' || type === 'user_leave') {
                messageClass = 'message system';
            }
            
            messageDiv.className = messageClass;
            
            const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            let displayMessage = message;
            let displaySender = sender;
            
            if (type === 'system' || type === 'user_join' || type === 'user_leave') {
                displaySender = '';
                displayMessage = message;
            }
            
            messageDiv.innerHTML = `
                <div class="message-content">${displayMessage}</div>
                <div class="message-info">
                    ${displaySender ? displaySender + ' • ' : ''}${timestamp}
                </div>
            `;
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // Enter key support
        document.getElementById('usernameInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                connect();
            }
        });

        document.getElementById('roomInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                connect();
            }
        });

        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Focus username input on load
        window.onload = function() {
            document.getElementById('usernameInput').focus();
        };
    