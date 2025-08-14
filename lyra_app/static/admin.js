const LYRA_API_URL = window.location.origin;

async function triggerLearning() {
    const res = await fetch(`${LYRA_API_URL}/learn`, { method: "POST" });
    const data = await res.json();
    alert(data.status);
}

async function fetchPrivateReport() {
    const res = await fetch(`${LYRA_API_URL}/daily_report`);
    const data = await res.json();
    document.getElementById("privateReport").innerText = data.report;
}

async function runTerminalCommand() {
    const cmd = document.getElementById("terminalCommand").value;
    const res = await fetch(`${LYRA_API_URL}/terminal`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ command: cmd })
    });
    const data = await res.json();
    const output = document.getElementById("terminal-output");
    output.innerHTML += `<div>$ ${cmd}<br>${data.output}</div>`;
}
