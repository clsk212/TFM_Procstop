// scripts.js

// Función para enviar un mensaje cuando el usuario presiona "Enter"
/*
function sendMessage(event) {
    if (event.keyCode === 13) {  // Detecta la tecla Enter
        let userInput = document.getElementById('userInput');
        if (userInput.value.trim() !== '') {
            displayMessage(userInput.value, 'user');
            userInput.value = '';  // Limpia el campo de entrada
            
            // Aquí podrías agregar la llamada AJAX al servidor para obtener una respuesta
            fetch('/get_response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userInput.value })
            })
            .then(response => response.json())
            .then(data => {
                displayMessage(data.message, 'bot');  // Suponiendo que la respuesta del servidor incluye un mensaje
            })
            .catch(error => console.error('Error:', error));
        }
    }
}
    */

// Función para mostrar mensajes en la pantalla
function displayMessage(message, sender) {
    let chatBox = document.getElementById('chatbox');
    let messageElement = document.createElement('p');
    messageElement.className = sender + "Text";  // Asigna la clase para el estilo
    messageElement.innerHTML = "<span>" + message + "</span>";
    chatBox.appendChild(messageElement);
}

// scripts.js

// Función para alternar la visibilidad del menú lateral
function toggleMenu() {
    let sideMenu = document.getElementById('side-menu');
    if (sideMenu.style.display === 'block') {
        sideMenu.style.display = 'none';
    } else {
        sideMenu.style.display = 'block';
    }
}
