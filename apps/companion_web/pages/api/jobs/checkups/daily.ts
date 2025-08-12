import type { NextApiRequest, NextApiResponse } from 'next';
import { allUsers, addMessage } from '../../../../server/companion/checkupsStore';
import { buildMessage } from '../../../../server/companion/messages';
import { gateCompanionMode } from '../../../../server/compliance/check';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.headers['x-admin-key'] !== process.env.ADMIN_DASH_KEY) {
    return res.status(401).json({ error: 'unauthorized' });
  }
  const store = await allUsers();
  let sent = 0;
  for (const [userId, rec] of Object.entries(store)) {
    if (rec.prefs.daily) {
      const mode = gateCompanionMode('therapy', rec.prefs.jurisdiction || 'US');
      const msg = buildMessage(rec.prefs.tone, mode);
      await addMessage(userId, msg);
      sent++;
    }
  }
  res.status(200).json({ sent });
}
