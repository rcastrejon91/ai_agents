const ADMIN_API_URL = window.location.hostname === "localhost" ? (window.BACKEND_URL || "http://localhost:5000") : "/api/lyra";

document.getElementById("getReportBtn").addEventListener("click", () => {
  fetch(`${ADMIN_API_URL}/daily_report`)
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("output").textContent = data.report;
    })
    .catch((err) => console.error(err));
});

document.getElementById("learnBtn").addEventListener("click", () => {
  fetch(`${ADMIN_API_URL}/learn`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("output").textContent = data.status;
    })
    .catch((err) => console.error(err));
});

document.getElementById("runTerminalBtn").addEventListener("click", () => {
  const code = document.getElementById("terminalInput").value;
  fetch(`${ADMIN_API_URL}/run_code`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("output").textContent = data.result || data.error;
    })
    .catch((err) => console.error(err));
});
