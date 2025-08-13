import type { NextApiRequest, NextApiResponse } from 'next';
import nodemailer from 'nodemailer';
import { createClient } from '@supabase/supabase-js';

const sb = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_ANON_KEY!);

async function mail(subject:string, html:string) {
  const t = nodemailer.createTransport({
    host: process.env.SMTP_HOST, port: Number(process.env.SMTP_PORT||587), secure: false,
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS }
  });
  await t.sendMail({ from: process.env.EMAIL_FROM, to: process.env.EMAIL_TO, subject, html });
}

export default async function handler(req:NextApiRequest, res:NextApiResponse) {
  if (req.headers['x-cron-key'] !== process.env.RESEARCH_CRON_SECRET) return res.status(401).json({ error:'unauthorized' });
  const { data: rows } = await sb.rpc('research_digest_last24');
  const html = `\n  <h3>Lyra Research Digest</h3>\n  <p>Here’s what I learned & proposed in the last 24h.</p>\n  <pre style="font-family:ui-monospace,monospace">${JSON.stringify(rows || [], null, 2)}</pre>\n  `;
  await mail('Lyra Research Digest', html);
  res.status(200).json({ ok:true });
}
