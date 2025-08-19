const LYRA_API_URL = window.location.hostname === "localhost" ? "http://localhost:5000" : "/api/lyra";
let isMuted = false;
let currentMood = "neutral";

function appendMessage(sender, message) {
  document.getElementById("chatLog").innerHTML +=
    `<p><b>${sender}:</b> ${message}</p>`;
}

// --- TEXT TO SPEECH ---
async function lyraSpeak(text, mood = currentMood) {
  if (isMuted) return;
  const res = await fetch(`${LYRA_API_URL}/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, mood }),
  });
  const audioBlob = await res.blob();
  const audioUrl = URL.createObjectURL(audioBlob);
  new Audio(audioUrl).play();
}

// --- SPEECH TO TEXT ---
async function lyraListen() {
  const res = await fetch(`${LYRA_API_URL}/listen`);
  const data = await res.json();
  appendMessage("You", data.transcript);
  return data.transcript;
}

// --- MUTE / UNMUTE ---
function toggleMute() {
  isMuted = !isMuted;
  console.log(`Muted: ${isMuted}`);
}

// --- CHANGE MOOD ---
function setMood(mood) {
  currentMood = mood;
}

// --- AUTO MOOD DETECTION ---
function autoDetectMood(message) {
  if (message.includes("sad")) currentMood = "calm";
  else if (message.includes("excited")) currentMood = "cheerful";
  else currentMood = "neutral";
}

document.getElementById("sendBtn").addEventListener("click", async () => {
  const input = document.getElementById("chatInput").value;
  autoDetectMood(input);
  appendMessage("You", input);
  await lyraSpeak(input);
  document.getElementById("chatInput").value = "";
});

document.getElementById("muteBtn").addEventListener("click", toggleMute);
