const LYRA_API_URL = "http://localhost:5000";
const ADMIN_KEY = "YOUR_SECRET_ADMIN_KEY";
let isMuted = false;
let currentMood = "neutral";

function appendMessage(sender, message) {
    const log = document.getElementById("chatLog");
    log.innerHTML += `<p><b>${sender}:</b> ${message}</p>`;
}

async function lyraSpeak(text, mood = "neutral") {
    if (isMuted) return;
    const res = await fetch(`${LYRA_API_URL}/speak`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, mood })
    });
    const audioBlob = await res.blob();
    new Audio(URL.createObjectURL(audioBlob)).play();
}

function toggleMute() {
    isMuted = !isMuted;
    document.getElementById("muteBtn").textContent = isMuted ? "Unmute" : "Mute";
}

function autoDetectMood(message) {
    if (message.includes("sad")) currentMood = "calm";
    else if (message.includes("excited")) currentMood = "cheerful";
    else currentMood = "neutral";
}

document.getElementById("sendBtn").addEventListener("click", async () => {
    const input = document.getElementById("chatInput").value;
    autoDetectMood(input);
    appendMessage("You", input);
    await lyraSpeak(input, currentMood);
});

document.getElementById("muteBtn").addEventListener("click", () => {
    toggleMute();
});

document.getElementById("runTerminalBtn").addEventListener("click", () => {
    const code = document.getElementById("terminalInput").value;
    fetch(`${LYRA_API_URL}/run_code`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Admin-Key": ADMIN_KEY
        },
        body: JSON.stringify({ code })
    })
    .then(res => res.json())
    .then(data => {
        appendMessage("Terminal Output", data.result || data.error);
    });
});

document.getElementById("getDailyReportBtn").addEventListener("click", () => {
    fetch(`${LYRA_API_URL}/daily_report`)
        .then(res => res.json())
        .then(data => {
            appendMessage("📅 Lyra Daily Report", data.report);
        });
});
