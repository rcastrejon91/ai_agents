import type { NextApiRequest, NextApiResponse } from "next";
import { getRobot } from "../../../../lib/robots";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { id } = req.query;
  const r = getRobot(String(id));
  if (!r) return res.status(404).json({ error: "robot_not_found" });
  return res.status(200).json({ robot: r });
}
