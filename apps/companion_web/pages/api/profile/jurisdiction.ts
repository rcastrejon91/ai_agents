import type { NextApiRequest, NextApiResponse } from "next";
import { setJur } from "../../../server/profile/store";

export default function handler(req: NextApiRequest, res: NextApiResponse){
  if (req.method !== "POST") return res.status(405).json({ error: "Use POST" });
  const userId = (req.headers["x-user-id"] || "anon").toString();
  const { jurisdiction } = req.body || {};
  if (!jurisdiction) return res.status(400).json({ error: "jurisdiction required (e.g., US-IL)" });
  const out = setJur(userId, jurisdiction.toUpperCase());
  // also set cookie for immediate effect
  res.setHeader("Set-Cookie", `jurisdiction=${encodeURIComponent(out.jurisdiction!)}; Path=/; Max-Age=${60*60*24*365}`);
  return res.status(200).json({ ok:true, jurisdiction: out.jurisdiction });
}
