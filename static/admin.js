document.getElementById("runCommand").addEventListener("click", () => {
    const cmd = document.getElementById("terminalCommand").value;
    fetch("/admin/terminal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("terminalOutput").innerText += data.output + "\n";
    });
});
