"use client";
import { useState } from "react";

export default function ScheduleCard({ device }: { device: { id: string } }) {
  const [cron, setCron] = useState("Sun 03:00");
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      await fetch("/api/devices/schedule", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ device_id: device.id, autoreboot_cron: cron }),
      });
      alert("Saved");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="rounded-lg border border-zinc-800 p-4">
      <div className="text-sm font-medium mb-2">Auto‑reboot schedule</div>
      <input
        className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-sm"
        value={cron}
        onChange={(e) => setCron(e.target.value)}
        placeholder="Daily 04:30 or Sun 03:00"
      />
      <button
        onClick={save}
        disabled={saving}
        className="mt-2 px-3 py-2 rounded bg-zinc-800 text-sm"
      >
        {saving ? "Saving…" : "Save"}
      </button>
      <div className="text-xs text-zinc-400 mt-2">
        Agent reads AUTOREBOOT_CRON env.
      </div>
    </div>
  );
}
