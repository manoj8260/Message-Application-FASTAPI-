// --- STATE & DOM ELEMENTS ---
let ws = null;
let username = '';
let currentRoom = '';
let roomHistories = {}; // { roomName: { messages: [], unread: 0 } }

const app = {
    loginSection: document.getElementById('loginSection'),
    messageForm: document.getElementById('messageForm'),
    messagesDiv: document.getElementById('messages'),
    roomListUl: document.getElementById('roomList'),
    connectionStatusDiv: document.getElementById('connectionStatus'),
    chatHeader: document.getElementById('chatHeader'),
    currentRoomName: document.getElementById('currentRoomName'),
    userProfile: document.getElementById('userProfile'),
    profileUsername: document.getElementById('profileUsername'),
    createRoomBtn: document.getElementById('createRoomBtn'),
    newRoomInput: document.getElementById('newRoomInput'),
    messageInput: document.getElementById('messageInput'),
    usernameInput: document.getElementById('usernameInput'),
    roomInput: document.getElementById('roomInput'),
    logoutBtn: document.getElementById('logoutBtn')
};

// --- WEBSOCKET & CONNECTION LOGIC ---

function connect() {
    const user = app.usernameInput.value.trim();
    const room = app.roomInput.value.trim() || 'general';
    
    if (!user) {
        alert('Please enter a username.');
        return;
    }

    username = user;
    app.profileUsername.textContent = username;
    app.userProfile.classList.remove('hidden');
    app.loginSection.classList.add('hidden');
    app.chatHeader.classList.remove('hidden');
    app.messageForm.classList.remove('hidden');
    switchRoom(room);
}

function switchRoom(roomName) {
    if (currentRoom === roomName && ws && ws.readyState === WebSocket.OPEN) return;

    if (ws) {
        ws.onclose = null;
        ws.close();
    }
    
    currentRoom = roomName;
    
    if (!roomHistories[roomName]) {
        roomHistories[roomName] = { messages: [], unread: 0 };
    }
    
    roomHistories[roomName].unread = 0; // Reset unread count on switch
    
    app.currentRoomName.textContent = roomName;
    updateRoomListUI();
    displayCurrentRoomMessages();
    joinRoom(roomName);
}

function joinRoom(roomName) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const backendHost = "localhost:8003"; 
    const wsUrl = `${wsProtocol}//${backendHost}/ws/${username}?room_id=${roomName}`;
    console.log(wsUrl)
    ws = new WebSocket(wsUrl);
    updateConnectionStatus(false, 'Connecting...');
    ws.onopen = () => {
        updateConnectionStatus(true, 'Connected');
        app.messageForm.classList.remove('hidden');
        app.messageInput.focus();
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const messageRoom = data.room_id || currentRoom;
        
        if (!roomHistories[messageRoom]) {
            roomHistories[messageRoom] = { messages: [], unread: 0 };
        }
        
        roomHistories[messageRoom].messages.push(data);
        
        if (messageRoom === currentRoom) {
            addMessageToUI(data);
        } else {
            roomHistories[messageRoom].unread++;
            updateRoomListUI();
        }
    };

    ws.onclose = () => updateConnectionStatus(false, 'Disconnected');
    ws.onerror = (error) => console.error('WebSocket Error:', error);
}

function sendMessage() {
    const message = app.messageInput.value.trim();
    if (!message || !ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(JSON.stringify({ message }));
    app.messageInput.value = '';
}

function logout() {
    if (ws) {
        ws.onclose = null;
        ws.close();
    }
    username = '';
    currentRoom = '';
    roomHistories = {};
    
    app.userProfile.classList.add('hidden');
    app.loginSection.classList.remove('hidden');
    app.chatHeader.classList.add('hidden');
    app.messageForm.classList.add('hidden');
    app.messagesDiv.innerHTML = '<div class="welcome-message"><p>You have been logged out.</p></div>';
    app.roomListUl.innerHTML = '';
}

// --- UI UPDATE FUNCTIONS ---

function updateConnectionStatus(connected, text) {
    const indicatorClass = connected ? 'online-indicator' : 'offline-indicator';
    app.connectionStatusDiv.innerHTML = `<span class="${indicatorClass}"></span>${text}`;
}

function updateRoomListUI() {
    app.roomListUl.innerHTML = '';
    for (const roomName in roomHistories) {
        const li = document.createElement('li');
        li.dataset.room = roomName;
        li.className = (roomName === currentRoom) ? 'active' : '';
        
        const roomText = document.createElement('span');
        roomText.textContent = roomName;
        li.appendChild(roomText);
        
        if (roomHistories[roomName].unread > 0) {
            const unread = document.createElement('span');
            unread.className = 'unread-indicator';
            li.appendChild(unread);
        }
        
        li.onclick = () => switchRoom(roomName);
        app.roomListUl.appendChild(li);
    }
}

function displayCurrentRoomMessages() {
    app.messagesDiv.innerHTML = '';
    const history = roomHistories[currentRoom]?.messages || [];
    if (history.length === 0) {
        app.messagesDiv.innerHTML = `<div class="welcome-message"><p>No messages in this room yet. Say hello!</p></div>`;
    } else {
        history.forEach(addMessageToUI);
    }
}

function addMessageToUI(data) {
    if (app.messagesDiv.querySelector('.welcome-message')) {
        app.messagesDiv.innerHTML = '';
    }

    const { username: sender, message, message_type = 'chat' } = data;
    const messageDiv = document.createElement('div');
    
    const messageClassMap = {
        'system': 'system',
        'user_join': 'system',
        'user_leave': 'system'
    };
    
    let messageTypeClass = messageClassMap[message_type] || (sender === username ? 'own' : 'other');
    messageDiv.className = `message ${messageTypeClass}`;
    
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute:'2-digit' });
    const displaySender = sender === username || messageTypeClass === 'system' ? '' : `<strong>${sender}</strong>`;

    messageDiv.innerHTML = `
        <div class="message-content">${message}</div>
        <div class="message-info">${displaySender} ${timestamp}</div>
    `;
    
    app.messagesDiv.appendChild(messageDiv);
    app.messagesDiv.scrollTop = app.messagesDiv.scrollHeight;
}

// --- EVENT LISTENERS ---

function setupEventListeners() {
    app.createRoomBtn.addEventListener('click', () => {
        const newRoomName = app.newRoomInput.value.trim();
        if (newRoomName && username) {
            switchRoom(newRoomName);
            app.newRoomInput.value = '';
        } else if (!username) {
            alert("Please log in first to create a room.");
        }
    });

    app.newRoomInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') app.createRoomBtn.click();
    });

    app.messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    app.logoutBtn.addEventListener('click', logout);
    
    app.roomInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') connect();
    });
}

// --- INITIALIZATION ---
window.onload = () => {
    app.usernameInput.focus();
    setupEventListeners();
};