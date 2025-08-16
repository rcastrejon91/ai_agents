import type { NextApiRequest, NextApiResponse } from "next";
import { verifyRegistrationResponse } from "@simplewebauthn/server";
import {
  addForUser,
  getChallenge,
} from "../../../../server/admin/webauthn/store";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  const email = (req.body?.email || "").toString();
  if (!email) return res.status(400).json({ error: "email required" });

  const expectedChallenge = getChallenge(email) || "";

  try {
    const verification = await verifyRegistrationResponse({
      response: req.body,
      expectedChallenge,
      expectedOrigin: process.env.ORIGIN || "",
      expectedRPID: process.env.RP_ID || "",
    });

    if (verification.verified && verification.registrationInfo) {
      const info = verification.registrationInfo;
      addForUser(email, {
        credentialId: info.credential.id,
        publicKey: Buffer.from(info.credential.publicKey).toString("base64url"),
        counter: info.credential.counter,
        transports: info.credential.transports as any,
        deviceName: req.body.deviceName || "Device",
        addedAt: Date.now(),
      });
    }

    res.status(200).json({ ok: verification.verified });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
}
