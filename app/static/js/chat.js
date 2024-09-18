function sendMessage() {
    var userInput = document.getElementById('userInput').value;
    
    if (!userInput.trim()) {
        alert("Por favor, ingresa un mensaje antes de enviar.");
        return;
    }
    
    document.getElementById('userInput').value = "";  // Limpia el campo de entrada inmediatamente después de enviar
    document.getElementById('userInput').disabled = true;  // Deshabilita el campo de entrada temporalmente
    
    document.getElementById('chatbox').innerHTML += '<p class="userText"><span>' + userInput + '</span></p>';
    scrollToBottom();  // Asegura que el chat se desplace hacia abajo

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('chatbox').innerHTML += '<p class="botText"><span>' + data.reply + '</span></p>';
        scrollToBottom();  // Asegura que el chat se desplace hacia abajo después de recibir la respuesta
        document.getElementById('userInput').disabled = false;  // Habilita nuevamente el campo de entrada
    })
    .catch(error => {
        console.log("Error: " + error);
        document.getElementById('userInput').disabled = false;  // Habilita en caso de error también
        scrollToBottom();
    });
}

function scrollToBottom() {
    var chatbox = document.getElementById('chatbox');
    chatbox.scrollTop = chatbox.scrollHeight;
}

function runScript(event) {
    if (event.keyCode == 13) {
        sendMessage();
        return false; // Previene la acción por defecto de un Enter en un input
    }
    return true;
}
