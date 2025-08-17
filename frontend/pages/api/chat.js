export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).end();
    return;
  }

  try {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000';
    const backendRes = await fetch(`${backendUrl}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body),
    });
    const data = await backendRes.json();
    res.status(200).json(data);
  } catch (err) {
    res.status(500).json({ error: "Failed to reach backend" });
  }
}
