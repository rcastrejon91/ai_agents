const LYRA_API_URL = window.location.origin;
let isMuted = false;

function appendMessage(sender, message) {
    const log = document.getElementById("chatLog");
    log.innerHTML += `<p><b>${sender}:</b> ${message}</p>`;
    log.scrollTop = log.scrollHeight;
}

document.getElementById("sendBtn").addEventListener("click", async () => {
    const input = document.getElementById("chatInput");
    const text = input.value.trim();
    if (!text) return;

    appendMessage("You", text);
    input.value = "";

    const res = await fetch(`${LYRA_API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    appendMessage("Lyra", data.response);

    if (!isMuted) {
        await fetch(`${LYRA_API_URL}/speak`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: data.response })
        });
    }
});

document.getElementById("muteBtn").addEventListener("click", () => {
    isMuted = !isMuted;
    document.getElementById("muteBtn").textContent = isMuted ? "🔊 Unmute" : "🔇 Mute";
});
