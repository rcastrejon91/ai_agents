import type { NextApiRequest, NextApiResponse } from "next";
import { roleFrom, limitGate } from "./_common";
import {
  isAllowed,
  banner,
  requireJurisdiction,
  redact,
} from "../../../server/legal/guardrails";
import fs from "fs";
import path from "path";

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
  const { type, facts = {}, jurisdiction } = (req.body as any) || {};
  if (!type) return res.status(400).json({ error: "type_required" });
  const { juris } = requireJurisdiction(jurisdiction);
  const gate = limitGate(req, res);
  res.setHeader("Set-Cookie", gate.setCookie);
  if (!gate.ok) {
    return res.status(402).json({
      error: "limit_reached",
      upgrade: process.env.BILLING_URL || null,
    });
  }
  const tplPath = path.join(
    process.cwd(),
    "server",
    "legal",
    "templates",
    `${type}.md`,
  );
  if (!fs.existsSync(tplPath))
    return res.status(400).json({ error: "unknown_template" });
  let template = fs.readFileSync(tplPath, "utf8");
  const placeholders = Array.from(template.matchAll(/{{(.*?)}}/g)).map(
    (m) => m[1],
  );
  const checklist: string[] = [];
  const allFacts: Record<string, string> = {
    ...facts,
    Jurisdiction: facts.Jurisdiction || juris,
  };
  placeholders.forEach((key) => {
    if (allFacts[key]) {
      template = template.replace(new RegExp(`{{${key}}}`, "g"), allFacts[key]);
    } else {
      template = template.replace(new RegExp(`{{${key}}}`, "g"), "[[BLANK]]");
      checklist.push(`Fill ${key}`);
    }
  });
  const draft = `${banner} Draft — Attorney Review Required\n\n${template}`;
  console.log("[LEGAL_AUDIT] draft", redact(JSON.stringify({ type, role })));
  return res.status(200).json({ draft, checklist });
}
