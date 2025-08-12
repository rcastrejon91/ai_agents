import type { NextApiRequest, NextApiResponse } from 'next';
import { listForUser, removeForUser } from '../../../../server/admin/webauthn/store';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const email = (req.query.email || req.body?.email || '').toString();
  if (!email) return res.status(400).json({ error: 'email required' });

  if (req.method === 'GET') {
    return res.status(200).json(listForUser(email));
  }

  if (req.method === 'DELETE') {
    const id = (req.query.id || req.body?.id || '').toString();
    if (!id) return res.status(400).json({ error: 'id required' });
    removeForUser(email, id);
    return res.status(200).json({ ok: true });
  }

  res.setHeader('Allow', 'GET,DELETE');
  return res.status(405).end();
}
