import type { NextApiRequest, NextApiResponse } from "next";

export default function handler(_req: NextApiRequest, res: NextApiResponse) {
  const key = process.env.OPENAI_API_KEY || "";
  res.status(200).json({
    ok: true,
    openai_key_present: Boolean(key),
    openai_key_tail: key ? key.slice(-4) : null,
    node_env: process.env.NODE_ENV,
  });
}

