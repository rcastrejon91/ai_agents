document.getElementById("runCommand").addEventListener("click", async () => {
    const cmd = document.getElementById("terminalCommand").value;
    const res = await fetch("/admin/terminal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd })
    });
    const data = await res.json();
    document.getElementById("terminalOutput").innerText += data.output + "\n";
});

document.getElementById("getReport").addEventListener("click", async () => {
    const res = await fetch("/daily_report");
    const data = await res.json();
    document.getElementById("reportOutput").innerText = data.report;
});
