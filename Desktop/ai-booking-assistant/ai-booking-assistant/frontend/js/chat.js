// =========================
// CONFIGURACIÓN
// =========================

const API_URL = 'http://localhost:5000/api';

// =========================
// REFERENCIAS DOM
// =========================

const chatContainer =
    document.getElementById('chatContainer');

const messageInput =
    document.getElementById('messageInput');

const sendButton =
    document.getElementById('sendButton');

const quickActions =
    document.getElementById('quickActions');

const loadingIndicator =
    document.getElementById('loadingIndicator');

// =========================
// ESTADO GLOBAL
// =========================

let isLoading = false;

// contexto completo conversación
let conversationContext = {
    history: []
};

// =========================
// INIT
// =========================

document.addEventListener('DOMContentLoaded', () => {

    initializeEventListeners();

    loadWelcomeMessage();

});

// =========================
// EVENTS
// =========================

function initializeEventListeners() {

    // botón enviar
    sendButton.addEventListener(
        'click',
        handleSendMessage
    );

    // enter enviar
    messageInput.addEventListener(
        'keypress',
        (e) => {

            if (
                e.key === 'Enter' &&
                !e.shiftKey
            ) {

                e.preventDefault();

                handleSendMessage();
            }

        }
    );

    // quick actions
    quickActions.addEventListener(
        'click',
        (e) => {

            if (
                e.target.classList.contains(
                    'quick-btn'
                )
            ) {

                const message =
                    e.target.getAttribute(
                        'data-message'
                    );

                messageInput.value = message;

                handleSendMessage();
            }

        }
    );

}

// =========================
// WELCOME
// =========================

function loadWelcomeMessage() {

    // opcional
    // ya existe en HTML

}

// =========================
// HANDLE MESSAGE
// =========================

async function handleSendMessage() {

    const message =
        messageInput.value.trim();

    if (!message || isLoading) return;

    // limpiar input
    messageInput.value = '';

    // render user
    appendMessage(message, 'user');

    // enviar backend
    await sendMessageToAPI(message);

}

// =========================
// API
// =========================

async function sendMessageToAPI(message) {

    isLoading = true;

    updateLoadingState(true);

    try {

        console.log(
            'CONTEXT ENVIADO:',
            conversationContext
        );

        const response = await fetch(
            `${API_URL}/chat`,
            {
                method: 'POST',

                headers: {
                    'Content-Type': 'application/json',
                },

                body: JSON.stringify({
                    message: message,
                    context: conversationContext
                })
            }
        );

        // =========================
        // ERROR HTTP
        // =========================

        if (!response.ok) {

            throw new Error(
                `HTTP ERROR ${response.status}`
            );

        }

        // =========================
        // JSON RESPONSE
        // =========================

        const data = await response.json();

        console.log(
            'RESPUESTA BACKEND:',
            data
        );

        // =========================
        // VALIDACIÓN
        // =========================

        if (!data.success) {

            throw new Error(
                data.message ||
                'Error backend'
            );

        }

        // =========================
        // GUARDAR CONTEXTO COMPLETO
        // =========================

        if (data.data) {

            conversationContext = data.data;

        }

        // asegurar history
        if (!conversationContext.history) {

            conversationContext.history = [];

        }

        console.log(
            'CONTEXT ACTUALIZADO:',
            conversationContext
        );

        // =========================
        // MOSTRAR RESPUESTA
        // =========================

        setTimeout(() => {

            appendMessage(
                data.message,
                'bot'
            );

            updateLoadingState(false);

            isLoading = false;

        }, 350);

    }

    catch (error) {

        console.error(
            'ERROR FRONT:',
            error
        );

        updateLoadingState(false);

        appendMessage(
            'Disculpá, hubo un problema de conexión 😅',
            'bot'
        );

        isLoading = false;

    }

}

// =========================
// RENDER MENSAJES
// =========================

function appendMessage(text, sender) {

    // remover welcome
    const welcomeMsg =
        chatContainer.querySelector(
            '.welcome-message'
        );

    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    // contenedor
    const messageDiv =
        document.createElement('div');

    messageDiv.className =
        `message ${sender}`;

    // contenido
    const contentDiv =
        document.createElement('div');

    contentDiv.className =
        'message-content';

    // soportar saltos línea
    contentDiv.innerHTML =
        text.replace(/\n/g, '<br>');

    // hora
    const timeDiv =
        document.createElement('div');

    timeDiv.className =
        'message-time';

    timeDiv.textContent =
        getCurrentTime();

    // append
    contentDiv.appendChild(timeDiv);

    messageDiv.appendChild(contentDiv);

    chatContainer.appendChild(messageDiv);

    // scroll auto
    scrollToBottom();

}

// =========================
// LOADING
// =========================

function updateLoadingState(loading) {

    if (loading) {

        loadingIndicator.classList.add(
            'active'
        );

        sendButton.disabled = true;

        messageInput.disabled = true;

    }

    else {

        loadingIndicator.classList.remove(
            'active'
        );

        sendButton.disabled = false;

        messageInput.disabled = false;

        messageInput.focus();

    }

}

// =========================
// SCROLL
// =========================

function scrollToBottom() {

    chatContainer.scrollTop =
        chatContainer.scrollHeight;

}

// =========================
// HORA
// =========================

function getCurrentTime() {

    const now = new Date();

    const hours =
        String(
            now.getHours()
        ).padStart(2, '0');

    const minutes =
        String(
            now.getMinutes()
        ).padStart(2, '0');

    return `${hours}:${minutes}`;

}

// =========================
// FORMAT DATE
// =========================

function formatDate(dateString) {

    const date = new Date(dateString);

    const options = {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    };

    return date.toLocaleDateString(
        'es-AR',
        options
    );

}