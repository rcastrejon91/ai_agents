import { useState, useEffect } from "react";
import { startRegistration } from "@simplewebauthn/browser";

export default function Passkeys() {
  const [email, setEmail] = useState("");
  const [devices, setDevices] = useState<any[]>([]);

  const load = async () => {
    if (!email) return;
    const res = await fetch(
      `/api/admin/webauthn/credentials?email=${encodeURIComponent(email)}`,
    );
    if (res.ok) setDevices(await res.json());
  };

  useEffect(() => {
    load();
  }, [email]);

  const registerDevice = async () => {
    const resp = await fetch(
      `/api/admin/webauthn/register-options?email=${encodeURIComponent(email)}`,
    );
    const opts = await resp.json();
    const att = await startRegistration(opts);
    await fetch("/api/admin/webauthn/register-verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...att, email }),
    });
    load();
  };

  const remove = async (id: string) => {
    await fetch(
      `/api/admin/webauthn/credentials?email=${encodeURIComponent(email)}&id=${encodeURIComponent(id)}`,
      {
        method: "DELETE",
      },
    );
    load();
  };

  return (
    <div>
      <h1>Passkeys</h1>
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="email"
      />
      <button onClick={registerDevice}>
        Register this device (Face ID/Touch ID)
      </button>
      <ul>
        {devices.map((d) => (
          <li key={d.credentialId}>
            {d.deviceName || d.credentialId}
            <button onClick={() => remove(d.credentialId)}>Remove</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
