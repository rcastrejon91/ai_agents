import type { NextApiRequest, NextApiResponse } from "next";
import { generateAuthenticationOptions } from "@simplewebauthn/server";
import {
  listForUser,
  setChallenge,
} from "../../../../server/admin/webauthn/store";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  const email = (req.query.username || "").toString();
  if (!email) return res.status(400).json({ error: "username required" });

  const creds = listForUser(email);
  if (!creds.length) return res.status(404).json({ error: "no credentials" });

  const options = await generateAuthenticationOptions({
    rpID: process.env.RP_ID || "localhost",
    allowCredentials: creds.map((c) => ({
      id: c.credentialId,
      transports: c.transports as any,
      type: "public-key",
    })),
  });

  setChallenge(email, options.challenge);
  res.status(200).json(options);
}
