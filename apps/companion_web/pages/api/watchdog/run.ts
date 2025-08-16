import type { NextApiRequest, NextApiResponse } from "next";
import { scanJurisdiction } from "../../../server/watchdog/scan";
import { applyPolicy } from "../../../server/watchdog/apply";
import { put } from "../../../server/watchdog/rulesStore";
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  if ((req.headers["x-admin-key"] || "") !== (process.env.ADMIN_DASH_KEY || ""))
    return res.status(401).json({ error: "unauthorized" });
  const jurs = req.body?.jurisdictions || ["US-IL", "US-CA", "US-FED"];
  const changes: any[] = [];
  for (const jur of jurs) {
    const s = await scanJurisdiction(jur);
    let parsed: any = {};
    try {
      parsed = JSON.parse(s.raw);
    } catch {}
    if (parsed?.domain && parsed?.status) {
      put({
        jur,
        domain: parsed.domain,
        status: parsed.status,
        summary: parsed.summary,
        sources: parsed.sources || [],
        effective_date: parsed.effective_date,
        hash: s.hash,
        ts: new Date().toISOString(),
      });
      applyPolicy(jur, parsed);
      changes.push({ jur, domain: parsed.domain, status: parsed.status });
    }
  }
  res.status(200).json({ ok: true, changes });
}
