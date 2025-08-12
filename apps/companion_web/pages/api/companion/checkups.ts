import type { NextApiRequest, NextApiResponse } from "next";
import { resolveJurisdiction } from "../../../server/compliance/jurisdiction";

function checkFeature(jur: string, feature: string) {
  return { allowed: true };
}

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const jur = resolveJurisdiction(req);
  const gate = checkFeature(jur, "companion.therapy");
  return res.status(200).json({ ok: true, gate, jurisdiction: jur });
}
