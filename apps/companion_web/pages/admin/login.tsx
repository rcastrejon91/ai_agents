import { useState, useEffect } from "react";
import { startAuthentication } from "@simplewebauthn/browser";

export default function AdminLogin() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [supports, setSupports] = useState(false);

  useEffect(() => {
    setSupports(typeof window !== "undefined" && !!window.PublicKeyCredential);
  }, []);

  const loginPassword = () => {
    // existing username/password + 2FA flow handled elsewhere
  };

  const loginPasskey = async () => {
    const optsRes = await fetch(
      `/api/admin/webauthn/auth-options?username=${encodeURIComponent(username)}`
    );
    if (!optsRes.ok) return;
    const opts = await optsRes.json();
    const asse = await startAuthentication(opts);
    const verify = await fetch("/api/admin/webauthn/auth-verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...asse, email: username }),
    });
    if (verify.ok) window.location.href = "/admin/health";
  };

  return (
    <div>
      <h1>Admin Login</h1>
      <input
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="password"
      />
      <button onClick={loginPassword}>Sign in</button>
      {supports && (
        <button onClick={loginPasskey}>Sign in with Face ID (Passkey)</button>
      )}
    </div>
  );
}
