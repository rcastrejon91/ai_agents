const LYRA_API_URL = window.location.origin;
let isMuted = false;
let currentMood = "neutral";

function appendMessage(sender, message) {
    const log = document.getElementById("chatLog");
    log.innerHTML += `<p><b>${sender}:</b> ${message}</p>`;
    log.scrollTop = log.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById("chatInput");
    const text = input.value.trim();
    if (!text) return;

    appendMessage("You", text);
    autoDetectMood(text);

    const res = await fetch(`${LYRA_API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
    });

    const data = await res.json();
    appendMessage("Lyra", data.reply);

    if (!isMuted) {
        await lyraSpeak(data.reply);
    }
    input.value = "";
}

async function lyraSpeak(text, mood = currentMood) {
    const res = await fetch(`${LYRA_API_URL}/speak`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, mood })
    });
    const audioBlob = await res.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    new Audio(audioUrl).play();
}

function autoDetectMood(message) {
    if (message.includes("sad")) currentMood = "calm";
    else if (message.includes("excited")) currentMood = "cheerful";
    else currentMood = "neutral";
}

document.getElementById("sendBtn").addEventListener("click", sendMessage);
document.getElementById("muteBtn").addEventListener("click", () => {
    isMuted = !isMuted;
    document.getElementById("muteBtn").textContent = isMuted ? "🔊 Unmute" : "🔇 Mute";
});
