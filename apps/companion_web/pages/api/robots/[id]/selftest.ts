import type { NextApiRequest, NextApiResponse } from "next";
import { getRobot } from "../../../../lib/robots";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { id } = req.query;
  const r = getRobot(String(id));
  if (!r) return res.status(404).json({ error: "robot_not_found" });

  // quick synthetic checks
  const checks = [
    { name: "motors", pass: r.health.motors === "ok" },
    { name: "cpu", pass: r.health.cpu === "ok" },
    { name: "temp", pass: r.health.tempC < 65 },
    { name: "battery", pass: r.battery > 10 },
  ];
  const ok = checks.every((c) => c.pass);
  return res
    .status(200)
    .json({ ok, checks, tempC: r.health.tempC, battery: r.battery });
}
