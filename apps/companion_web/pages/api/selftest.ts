import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  _req: NextApiRequest,
  res: NextApiResponse,
) {
  const key = process.env.OPENAI_API_KEY;
  if (!key)
    return res
      .status(500)
      .json({ ok: false, step: "env", msg: "No OPENAI_API_KEY" });

  try {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${key}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [{ role: "user", content: "ping" }],
      }),
    });

    const text = await response.text();
    
    if (response.ok) {
      console.log("OpenAI self-test successful");
      return res.status(200).json({ 
        ok: true, 
        status: response.status, 
        body: text.slice(0, 500) 
      });
    } else {
      console.error("OpenAI self-test failed", { status: response.status, error: text });
      return res.status(502).json({ 
        ok: false, 
        status: response.status, 
        body: text.slice(0, 500) 
      });
    }
  } catch (error) {
    console.error("Self-test exception", error);
    return res.status(500).json({ 
      ok: false, 
      step: "request", 
      msg: "Request failed" 
    });
  }
}
