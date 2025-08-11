import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs/promises';
import path from 'path';
import { isAllowed, banner, requireJurisdiction, redact, shouldRefuse } from '../../../../../server/legal/guardrails';
import { roleFrom, checkLimit } from './_common';

const TEMPLATES_DIR = path.join(process.cwd(), 'server', 'legal', 'templates');
const TYPES = ['NDA_basic', 'Engagement_Letter', 'Demand_Letter'];

function fillTemplate(t: string, facts: Record<string, any>): string {
  return t.replace(/{{(\w+)}}/g, (_, k) => (facts[k] ? String(facts[k]) : `[${k}]`));
}

function checkList(type: string): string[] {
  switch (type) {
    case 'NDA_basic':
      return ['Confirm party names and signatures', 'Review confidentiality term and jurisdiction'];
    case 'Engagement_Letter':
      return ['Verify scope of representation', 'Confirm fee arrangement'];
    case 'Demand_Letter':
      return ['Validate factual background', 'Confirm legal claims'];
    default:
      return [];
  }
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const role = roleFrom(req);
  if (!isAllowed(role)) return res.status(403).json({ error: 'forbidden' });

  const { type, facts = {}, jurisdiction } = (req.body as any) || {};
  if (!type || !TYPES.includes(type)) return res.status(400).json({ error: 'unsupported type' });

  if (shouldRefuse('draft', role)) {
    return res.status(403).json({ error: 'refused', message: 'Please escalate to an attorney.' });
  }

  if (!checkLimit(req, res)) return;

  const { juris, note } = requireJurisdiction(jurisdiction);
  const filePath = path.join(TEMPLATES_DIR, `${type}.md`);
  let template = '';
  try {
    template = await fs.readFile(filePath, 'utf8');
  } catch {
    return res.status(500).json({ error: 'template missing' });
  }

  const draftBody = fillTemplate(template, { ...facts, Jurisdiction: juris });
  const draft = `${banner} Draft—Attorney Review Required\n\n${note}\n\n${draftBody}`;

  console.log(`[LEGAL_AUDIT] draft role=${role} type=${type} juris=${juris} facts=${redact(JSON.stringify(facts))}`);

  return res.status(200).json({ draft, checkList: checkList(type) });
}
