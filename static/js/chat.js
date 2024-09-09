function sendMessage() {
    var userInput = document.getElementById('userInput').value;
    
    if (!userInput.trim()) {
        alert("Por favor, ingresa un mensaje antes de enviar.");
        return;
    }
    
    document.getElementById('chatbox').innerHTML += '<p class="userText"><span>' + userInput + '</span></p>';

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
        console.log(data);
        document.getElementById('userInput').value = "";  // Limpia el campo de entrada después de enviar
    })
    .catch(error => {
        console.log("Error: " + error);
    });




    /*

    */
}

function runScript(event) {
    if (event.keyCode == 13) {
        sendMessage();
        return false; // Previene la acción por defecto de un Enter en un input
    }
    return true;
}
