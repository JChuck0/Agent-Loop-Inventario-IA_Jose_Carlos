// ==========================================
// CONFIGURACIÓN
// ==========================================

const API_URL = "https://super-system-rqp9qq5rrx9fp654-8000.app.github.dev/agent/chat";


// ==========================================
// DOM
// ==========================================

const form = document.getElementById("message-form");
const input = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const messages = document.getElementById("messages");
const conversation = document.getElementById("conversation");


// ==========================================
// ESTADO
// ==========================================

let isProcessing = false;


// ==========================================
// CREAR MENSAJES
// ==========================================

function createMessage(role, text) {

    const wrapper = document.createElement("div");

    const card = document.createElement("div");

    const label = document.createElement("div");

    const content = document.createElement("p");


    const isUser = role === "USER";

    const isError = role === "SYSTEM ERROR";


    // USER derecha
    // AGENT y SYSTEM izquierda

    wrapper.className = isUser
        ? "flex justify-end"
        : "flex justify-start";


    // Estilos generales de la tarjeta

    card.className = `
        w-fit
        max-w-[90%]
        sm:max-w-[75%]
        md:max-w-[65%]

        border

        bg-black

        px-4
        py-3

        shadow-[0_0_8px_rgba(74,222,128,0.08)]

        transition-all
        duration-200
    `;


    // Estilo de error

    if (isError) {

        card.classList.add(
            "border-red-500/80",
            "text-red-300"
        );

        label.className = `
            mb-2

            text-[11px]
            font-bold

            tracking-[0.18em]

            text-red-500
        `;

    } else {

        card.classList.add(
            "border-green-500/60",
            "text-green-200"
        );

        label.className = `
            mb-2

            text-[11px]
            font-bold

            tracking-[0.18em]

            text-green-500
        `;
    }


    label.textContent = role;


    content.className = `
        text-sm
        sm:text-base

        leading-relaxed

        whitespace-pre-wrap
        break-words
    `;


    content.textContent = text;


    card.appendChild(label);

    card.appendChild(content);

    wrapper.appendChild(card);

    messages.appendChild(wrapper);


    scrollToBottom();
}


// ==========================================
// PROCESSING
// ==========================================

function showProcessing() {

    const wrapper = document.createElement("div");

    wrapper.id = "processing-message";

    wrapper.className = "flex justify-start";


    const card = document.createElement("div");

    card.className = `
        border
        border-green-500/40

        bg-black

        px-4
        py-3

        text-sm
        text-green-500

        shadow-[0_0_8px_rgba(74,222,128,0.08)]
    `;


    const label = document.createElement("div");

    label.className = `
        mb-2

        text-[11px]
        font-bold

        tracking-[0.18em]

        text-green-600
    `;

    label.textContent = "AGENT";


    const processing = document.createElement("p");

    processing.innerHTML = `
        &gt; PROCESSING
        <span class="animate-pulse">█</span>
    `;


    card.appendChild(label);

    card.appendChild(processing);

    wrapper.appendChild(card);

    messages.appendChild(wrapper);


    scrollToBottom();
}


function removeProcessing() {

    const processingMessage =
        document.getElementById("processing-message");


    if (processingMessage) {

        processingMessage.remove();
    }
}


// ==========================================
// ESTADO DE INTERFAZ
// ==========================================

function setProcessingState(processing) {

    isProcessing = processing;

    sendButton.disabled = processing;

    input.disabled = processing;


    if (processing) {

        showProcessing();

    } else {

        removeProcessing();
    }
}


// ==========================================
// SCROLL
// ==========================================

function scrollToBottom() {

    conversation.scrollTo({

        top: conversation.scrollHeight,

        behavior: "smooth"
    });
}


// ==========================================
// PETICIÓN A FASTAPI
// ==========================================

async function sendMessage(message) {

    const response = await fetch(API_URL, {

        method: "POST",

        headers: {

            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            message: message
        })
    });


    if (!response.ok) {

        throw new Error(
            `Server responded with status ${response.status}`
        );
    }


    let data;


    try {

        data = await response.json();

    } catch {

        throw new Error(
            "Invalid JSON response."
        );
    }


    if (
        !data ||
        typeof data.message !== "string"
    ) {

        throw new Error(
            "Response does not contain a valid message."
        );
    }


    return data.message;
}


// ==========================================
// FORMULARIO
// ==========================================

async function handleSubmit(event) {

    event.preventDefault();


    if (isProcessing) {

        return;
    }


    const message = input.value.trim();


    if (!message) {

        return;
    }


    // Mostrar mensaje USER

    createMessage(
        "USER",
        message
    );


    // Limpiar campo

    input.value = "";


    // Mostrar PROCESSING

    setProcessingState(true);


    try {

        const agentResponse =
            await sendMessage(message);


        setProcessingState(false);


        createMessage(
            "AGENT",
            agentResponse
        );

    } catch (error) {

        console.error(error);


        setProcessingState(false);


        createMessage(
            "SYSTEM ERROR",
            "Unable to reach inventory server."
        );
    }


    input.focus();
}


// ==========================================
// EVENTOS
// ==========================================

form.addEventListener(
    "submit",
    handleSubmit
);


input.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            form.requestSubmit();
        }
    }
);


// ==========================================
// INICIO
// ==========================================

window.addEventListener(
    "DOMContentLoaded",
    function () {

        input.focus();
    }
);