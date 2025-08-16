import { useEffect, useState } from "react";
export default function Compliance() {
  const [map, setMap] = useState<any>({});
  const [rows, setRows] = useState<any[]>([]);
  const key = process.env.NEXT_PUBLIC_ADMIN_UI_KEY || "";
  useEffect(() => {
    fetch("/api/compliance/policies")
      .then((r) => r.json())
      .then(setMap);
    fetch("/api/compliance/rules")
      .then((r) => r.json())
      .then((d) => setRows(d.rows));
  }, []);
  async function run() {
    await fetch("/api/watchdog/run", {
      method: "POST",
      headers: { "x-admin-key": key, "Content-Type": "application/json" },
      body: JSON.stringify({ jurisdictions: ["US-IL", "US-CA", "US-FED"] }),
    });
    location.reload();
  }
  return (
    <main style={{ padding: 24 }}>
      <h1>Compliance Dashboard</h1>
      <button onClick={run}>Run Watchdog Scan Now</button>
      <h3 style={{ marginTop: 16 }}>Current Policies</h3>
      <pre>{JSON.stringify(map, null, 2)}</pre>
      <h3>Recent Rule Updates</h3>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>When</th>
            <th>Jurisdiction</th>
            <th>Domain</th>
            <th>Status</th>
            <th>Summary</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 50).map((r, i) => (
            <tr key={i} style={{ borderTop: "1px solid #333" }}>
              <td>{r.ts}</td>
              <td>{r.jur}</td>
              <td>{r.domain}</td>
              <td>{r.status}</td>
              <td style={{ maxWidth: 480, whiteSpace: "pre-wrap" }}>
                {r.summary}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
