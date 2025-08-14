const LYRA_API_URL = window.location.origin;

document.getElementById("fetchReportBtn").addEventListener("click", async () => {
    const res = await fetch(`${LYRA_API_URL}/daily_report`);
    const data = await res.json();
    document.getElementById("reportOutput").textContent = data.report;
});

document.getElementById("runCmdBtn").addEventListener("click", async () => {
    const cmd = document.getElementById("terminalInput").value;
    const res = await fetch(`${LYRA_API_URL}/admin/terminal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd })
    });
    const data = await res.json();
    document.getElementById("terminalOutput").textContent = data.output;
});
