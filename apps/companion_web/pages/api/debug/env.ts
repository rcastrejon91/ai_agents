import type { NextApiRequest, NextApiResponse } from "next";

// Temporary endpoint to verify environment wiring and network access.
export default async function handler(
  _req: NextApiRequest,
  res: NextApiResponse
) {
  const key = process.env.OPENAI_API_KEY;
  const hasKey = !!key;
  const tail = key ? key.slice(-4) : null;

  // Don’t print full key. Only show last 4 to verify wiring.
  return res.status(200).json({
    ok: true,
    openai_key_present: hasKey,
    openai_key_tail: tail,
    node_env: process.env.NODE_ENV,
    vercel_env: process.env.VERCEL_ENV, // "development" | "preview" | "production"
  });
}
