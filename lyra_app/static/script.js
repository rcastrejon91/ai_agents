document.getElementById("sendBtn").addEventListener("click", () => {
    const msg = document.getElementById("chatInput").value;
    const log = document.getElementById("chatLog");
    log.innerHTML += `<p><b>You:</b> ${msg}</p>`;
    fetch("/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: msg })
    });
});
