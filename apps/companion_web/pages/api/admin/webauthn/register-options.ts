import type { NextApiRequest, NextApiResponse } from 'next';
import { generateRegistrationOptions } from '@simplewebauthn/server';
import { listForUser, setChallenge } from '../../../../server/admin/webauthn/store';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const email = (req.query.email || '').toString();
  if (!email) return res.status(400).json({ error: 'email required' });

  const rpName = process.env.RP_NAME || 'AITaskFlo Admin';
  const rpID = process.env.RP_ID || 'localhost';

  const options = await generateRegistrationOptions({
    rpName,
    rpID,
    userID: Buffer.from(email, 'utf8'),
    userName: email,
    attestationType: 'none',
    excludeCredentials: listForUser(email).map(c => ({
      id: c.credentialId,
      type: 'public-key',
    })),
  });

  setChallenge(email, options.challenge);
  res.status(200).json(options);
}
