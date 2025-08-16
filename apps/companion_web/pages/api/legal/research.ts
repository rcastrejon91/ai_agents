import type { NextApiRequest, NextApiResponse } from "next";
import { roleFrom, tavilySearch, openaiSummarize, limitGate } from "./_common";
import {
  isAllowed,
  banner,
  requireJurisdiction,
  shouldRefuse,
  redact,
} from "../../../server/legal/guardrails";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  if (req.method !== "POST")
    return res.status(405).json({ error: "method_not_allowed" });
  const role = roleFrom(req);
  if (!isAllowed(role)) {
    return res
      .status(403)
      .json({ error: "unauthorized", message: "For internal use only." });
  }
  const { query, jurisdiction, intent = "research" } = (req.body as any) || {};
  if (!query || typeof query !== "string")
    return res.status(400).json({ error: "query_required" });
  if (shouldRefuse(intent, role))
    return res.status(403).json({ error: "unauthorized" });
  const { juris, note } = requireJurisdiction(jurisdiction);
  const gate = limitGate(req, res);
  res.setHeader("Set-Cookie", gate.setCookie);
  if (!gate.ok) {
    return res
      .status(402)
      .json({
        error: "limit_reached",
        upgrade: process.env.BILLING_URL || null,
      });
  }
  const search = await tavilySearch(query);
  const prompt =
    `Summarize the following legal research for jurisdiction ${juris} with numbered citations like [1].\n` +
    search.results
      .map((r: any, i: number) => `[${i + 1}] ${r.title} - ${r.snippet}`)
      .join("\n");
  const body = await openaiSummarize(prompt);
  const summary = `${banner}\n${note}\n\n${body}`;
  const citations = search.results.map((r: any) => ({
    title: r.title,
    url: r.url,
  }));
  console.log(
    "[LEGAL_AUDIT] research",
    redact(JSON.stringify({ query, role })),
  );
  return res.status(200).json({ summary, citations });
}
