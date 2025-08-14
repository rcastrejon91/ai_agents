const ADMIN_API_URL = "http://localhost:5000";

document.getElementById("getReportBtn").addEventListener("click", () => {
    fetch(`${ADMIN_API_URL}/daily_report`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("output").textContent = data.report;
        })
        .catch(err => console.error(err));
});

document.getElementById("learnBtn").addEventListener("click", () => {
    fetch(`${ADMIN_API_URL}/learn`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
            document.getElementById("output").textContent = data.status;
        })
        .catch(err => console.error(err));
});

document.getElementById("runTerminalBtn").addEventListener("click", () => {
    const command = document.getElementById("terminalInput").value;
    fetch(`${ADMIN_API_URL}/admin/terminal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("output").textContent = data.output;
    })
    .catch(err => console.error(err));
});
