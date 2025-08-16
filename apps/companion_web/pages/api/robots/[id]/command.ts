import type { NextApiRequest, NextApiResponse } from "next";
import { getRobot, goto } from "../../../../lib/robots";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  const { id } = req.query;
  if (req.method !== "POST")
    return res.status(405).json({ error: "Method not allowed" });
  const { cmd, args } = req.body || {};
  const r = getRobot(String(id));
  if (!r) return res.status(404).json({ error: "robot_not_found" });

  if (cmd === "goto") {
    const wp = args?.waypoint;
    if (!wp) return res.status(400).json({ error: "waypoint required" });
    const out = goto(r.id, wp);
    return res.status(200).json({ ok: out.accepted, eta_s: out.eta_s });
  }
  return res.status(400).json({ error: "unknown_cmd" });
}
