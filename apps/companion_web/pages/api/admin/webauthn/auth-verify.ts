import type { NextApiRequest, NextApiResponse } from "next";
import { verifyAuthenticationResponse } from "@simplewebauthn/server";
import {
  getChallenge,
  listForUser,
  updateCounter,
} from "../../../../server/admin/webauthn/store";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const email = (req.body?.email || "").toString();
  if (!email) return res.status(400).json({ error: "email required" });

  const expectedChallenge = getChallenge(email) || "";
  const creds = listForUser(email);
  const credential = creds.find((c) => c.credentialId === req.body.id);
  if (!credential) return res.status(400).json({ error: "unknown credential" });

  try {
    const verification = await verifyAuthenticationResponse({
      response: req.body,
      expectedChallenge,
      expectedOrigin: process.env.ORIGIN || "",
      expectedRPID: process.env.RP_ID || "",
      credential: {
        id: credential.credentialId,
        publicKey: Buffer.from(credential.publicKey, "base64url"),
        counter: credential.counter,
        transports: credential.transports as any,
      },
    });

    if (verification.verified) {
      updateCounter(
        email,
        credential.credentialId,
        verification.authenticationInfo.newCounter
      );
      // TODO: start admin session using existing cookie mechanism
    }

    res.status(200).json({ ok: verification.verified });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
}
