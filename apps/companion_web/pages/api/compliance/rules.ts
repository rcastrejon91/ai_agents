import type { NextApiRequest, NextApiResponse } from "next";
import { all } from "../../../server/watchdog/rulesStore";
export default function handler(req:NextApiRequest,res:NextApiResponse){
  const jur = (req.query.jurisdiction||"").toString();
  const rows = all().filter(r=>!jur || r.jur===jur);
  res.status(200).json({ rows });
}
