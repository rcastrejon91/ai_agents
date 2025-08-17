const ADMIN_API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5000";

// Helper function to make API calls with timeout and error handling
async function makeApiCall(url, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error.name === 'AbortError') {
      throw new Error('Request timeout - server is not responding');
    }
    throw error;
  }
}

document.getElementById("getReportBtn").addEventListener("click", () => {
  makeApiCall(`${ADMIN_API_URL}/daily_report`)
    .then((data) => {
      document.getElementById("output").textContent = data.report;
    })
    .catch((err) => {
      console.error(err);
      document.getElementById("output").textContent = `Error: ${err.message}`;
    });
});

document.getElementById("learnBtn").addEventListener("click", () => {
  makeApiCall(`${ADMIN_API_URL}/learn`, { method: "POST" })
    .then((data) => {
      document.getElementById("output").textContent = data.status;
    })
    .catch((err) => {
      console.error(err);
      document.getElementById("output").textContent = `Error: ${err.message}`;
    });
});

document.getElementById("runTerminalBtn").addEventListener("click", () => {
  const code = document.getElementById("terminalInput").value;
  makeApiCall(`${ADMIN_API_URL}/run_code`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  })
    .then((data) => {
      document.getElementById("output").textContent = data.result || data.error;
    })
    .catch((err) => {
      console.error(err);
      document.getElementById("output").textContent = `Error: ${err.message}`;
    });
});
