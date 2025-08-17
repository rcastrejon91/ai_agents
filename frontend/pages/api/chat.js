import { config } from "../../config";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).end();
    return;
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

    const backendRes = await fetch(`${config.backendUrl}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!backendRes.ok) {
      throw new Error(`Backend responded with status: ${backendRes.status}`);
    }

    const data = await backendRes.json();
    res.status(200).json(data);
  } catch (err) {
    if (err.name === 'AbortError') {
      res.status(500).json({ error: "Request timeout - backend server is not responding" });
    } else {
      console.error('Backend API error:', err);
      res.status(500).json({ error: "Failed to reach backend" });
    }
  }
}
