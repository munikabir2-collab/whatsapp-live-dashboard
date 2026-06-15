const ws = new WebSocket("ws://127.0.0.1:8000/ws");

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.type === "status_update") {
        document.getElementById("msg-" + data.id).innerText =
            "Status: " + data.status;
    }

    if (data.type === "new_message") {
        const div = document.createElement("div");
        div.innerHTML = `
            <p>${data.text}</p>
            <span>${data.status}</span>
        `;
        document.getElementById("messages").appendChild(div);
    }
};