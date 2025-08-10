"use client";
import { useState } from "react";
import { loadStripe } from "@stripe/stripe-js";
// put your publishable key in Vercel env as NEXT_PUBLIC_STRIPE_PK
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PK!);

export default function Home() {
  const [log, setLog] = useState<{role:"you"|"ai";text:string}[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  async function send() {
    if (!input.trim()) return;
    const msg = input.trim();
    setInput("");
    setLog(l => [...l, {role:"you", text: msg}]);
    setBusy(true);
    try {
      const r = await fetch(process.env.NEXT_PUBLIC_API_URL + "/chat", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ message: msg })
      });
      const data = await r.json();
      setLog(l => [...l, {role:"ai", text: data.text || "(no reply)"}]);
    } finally { setBusy(false); }
  }

  function checkout(){
    (async () => {
      const r = await fetch(process.env.NEXT_PUBLIC_API_URL + "/billing/checkout", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        // include email if you collect it on page; otherwise omit body
        body: JSON.stringify({ /* customer_email: "test@example.com" */ })
      });
      const data = await r.json();
      if (data.url) {
        // simplest: redirect to hosted checkout
        window.location.href = data.url;
        return;
      }
      // or use stripe.js if you want
      const stripe = await stripePromise;
      await stripe?.redirectToCheckout({ sessionId: data.sessionId });
    })();
  }

  return (
    <main className="mx-auto max-w-xl p-6">
      <h1 className="text-2xl font-semibold mb-2">Nova — Companion (Founders Preview)</h1>
      <p className="text-sm text-gray-500 mb-4">
        Chat with Nova. Want full access? <button onClick={checkout} className="underline">Get Founders Pass</button>
      </p>

      <div className="border rounded p-3 h-96 overflow-y-auto bg-white">
        {log.map((m,i)=>(
          <div key={i} className="mb-3">
            <div className="text-xs text-gray-400">{m.role==="you"?"You":"Nova"}</div>
            <div>{m.text}</div>
          </div>
        ))}
        {busy && <div className="text-sm text-gray-400">Nova is typing…</div>}
      </div>

      <div className="mt-3 flex gap-2">
        <input className="flex-1 border rounded px-3 py-2"
          placeholder="Type a message"
          value={input}
          onChange={e=>setInput(e.target.value)}
          onKeyDown={e=>e.key==="Enter"&&send()}
        />
        <button onClick={send} disabled={busy}
          className="px-4 py-2 rounded bg-black text-white disabled:opacity-50">
          Send
        </button>
      </div>
    </main>
  );
}
