import type { NextApiRequest, NextApiResponse } from 'next';
import { getPrefs, savePrefs, addMessage, CheckupPrefs } from '../../../server/companion/checkupsStore';
import { buildMessage } from '../../../server/companion/messages';
import { gateCompanionMode } from '../../../server/compliance/check';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const userId = req.headers['x-user-id'] as string | undefined;
  if (!userId) return res.status(400).json({ error: 'missing user id' });

  if (req.method === 'GET') {
    const prefs = await getPrefs(userId);
    return res.status(200).json(prefs || {});
  }

  if (req.method === 'POST') {
    const body = req.body as CheckupPrefs;
    const jurisdiction = (req.headers['x-jurisdiction'] as string) || body.jurisdiction;
    await savePrefs(userId, { ...body, jurisdiction });
    return res.status(200).json({ ok: true });
  }

  if (req.method === 'PUT') {
    const tone = (req.body && req.body.tone) || 'kind';
    const jurisdiction = (req.headers['x-jurisdiction'] as string) || 'US';
    const mode = gateCompanionMode('therapy', jurisdiction);
    const message = buildMessage(tone, mode);
    if (!('preview' in req.query)) {
      await addMessage(userId, message);
    }
    return res.status(200).json({ sent: !('preview' in req.query), mode, message });
  }

  res.setHeader('Allow', ['GET', 'POST', 'PUT']);
  return res.status(405).end();
}
