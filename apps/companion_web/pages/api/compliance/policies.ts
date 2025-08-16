import type { NextApiRequest, NextApiResponse } from "next";
import map from "../../../server/compliance/state_policies.json";
export default function handler(_req: NextApiRequest, res: NextApiResponse) {
  res.status(200).json(map);
}
