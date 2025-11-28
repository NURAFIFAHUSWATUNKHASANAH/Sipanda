const menuIcon = document.getElementById("menu-icon");
const menuList = document.getElementById("menu-list");

menuIcon.addEventListener("click", () => {
    menuList.classList.toggle("hidden");
});


// JavaScript untuk mengendalikan dropdown profil
document.getElementById("profileBtn").addEventListener("click", function (e) {
    e.preventDefault();  // Mencegah link default
    var dropdown = document.getElementById("profileDropdown");
    dropdown.style.display = (dropdown.style.display === "block") ? "none" : "block";
});

// Menutup dropdown ketika mengklik di luar area dropdown
window.onclick = function (event) {
    if (!event.target.matches('#profileBtn')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.style.display === "block") {
                openDropdown.style.display = "none";
            }
        }
    }
}

class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('#send-btn'), // Ganti dengan ID baru
            inputField: document.querySelector('#user-input'), // Ganti dengan ID baru
            chatMessages: document.querySelector('.chat-messages'), // Tambahkan elemen baru
        };

        this.state = false;
        this.messages = []; // Menyimpan pesan
    }

    display() {
        const { openButton, chatBox, sendButton, inputField } = this.args;

        // Event untuk membuka dan menutup chatbox
        openButton.addEventListener('click', () => this.toggleState(chatBox));

        // Event untuk tombol kirim
        sendButton.addEventListener('click', () => this.onSendButton());

        // Event untuk tombol "Enter" pada input field
        inputField.addEventListener('keyup', ({ key }) => {
            if (key === 'Enter') {
                this.onSendButton();
            }
        });
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // Tampilkan atau sembunyikan chatbox
        if (this.state) {
            chatbox.classList.add('chatbox--active');
        } else {
            chatbox.classList.remove('chatbox--active');
        }
    }

    onSendButton() {
        const { inputField, chatMessages } = this.args;
        const userMessage = inputField.value.trim();

        if (!userMessage) return; // Jangan kirim pesan kosong

        // Tambahkan pesan pengguna ke UI
        this.addMessageToChatbox(chatMessages, 'User', userMessage);

        // Kirim pesan ke API chatbot
        fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMessage }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                const botResponse = data.response || 'Maaf, terjadi kesalahan pada server.';
                this.addMessageToChatbox(chatMessages, 'Si Panda', botResponse, true);
                inputField.value = ''; // Kosongkan input pengguna
            })
            .catch((error) => {
                console.error('Error:', error);
                this.addMessageToChatbox(chatMessages, 'Si Panda', 'Maaf, tidak dapat terhubung ke server.', true);
                inputField.value = ''; // Kosongkan input pengguna
            });
    }

    addMessageToChatbox(chatMessages, sender, message, isBot = false) {
        if (isBot) {
            // Tambahkan pesan bot dengan avatar
            const botMessageElement = document.createElement('div');
            botMessageElement.classList.add('message');
            botMessageElement.innerHTML = `  
                <div class="message received">
                    <p>${message}</p>
                </div>`;
            chatMessages.appendChild(botMessageElement);
        } else {
            // Tambahkan pesan pengguna
            const userMessageElement = document.createElement('div');
            userMessageElement.classList.add('message', 'sent');
            userMessageElement.innerHTML = `<p>${message}</p>`;
            chatMessages.appendChild(userMessageElement);
        }

        // Scroll otomatis ke bagian bawah
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

}

// Inisialisasi class Chatbox
const chatbox = new Chatbox();
chatbox.display();