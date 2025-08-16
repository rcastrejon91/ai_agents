"use client";
import { useEffect, useState } from "react";
import PairForm from "./_components/PairForm";
import DeviceList from "./_components/DeviceList";
import CommandButtons from "./_components/CommandButtons";
import ScheduleCard from "./_components/ScheduleCard";
import HealthCard from "./_components/HealthCard";

type Device = {
  id: string;
  public_name: string;
  owner_email: string;
  model?: string;
  last_seen?: number;
};

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [selected, setSelected] = useState<Device | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<string | null>(null);

  async function load() {
    try {
      const r = await fetch("/api/devices/list", { cache: "no-store" });
      const j = await r.json();
      setDevices(j.devices || []);
      if (!selected && j.devices?.length) setSelected(j.devices[0]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Devices</h1>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-4">
          <DeviceList
            devices={devices}
            selectedId={selected?.id || null}
            onSelect={(d) => setSelected(d)}
            loading={loading}
            onRefresh={load}
          />
          {selected && (
            <div className="grid sm:grid-cols-2 gap-4">
              <CommandButtons
                device={selected}
                onDone={() => setToast("Command sent. Check email to confirm.")}
              />
              <ScheduleCard device={selected} />
              <HealthCard device={selected} />
            </div>
          )}
        </div>

        <div className="space-y-4">
          <PairForm
            onPaired={() => {
              setToast("Device paired. Copy the ID/secret for the agent.");
              load();
            }}
          />
          <div className="rounded-lg border border-zinc-800 p-4 text-sm">
            <div className="font-medium mb-1">Docker agent</div>
            <pre className="text-xs overflow-auto">
              {`docker compose up -d
# set env:
# LYRA_HOST, DEVICE_ID, DEVICE_SECRET`}
            </pre>
          </div>
        </div>
      </div>

      {toast && (
        <div
          className="fixed bottom-4 right-4 bg-emerald-600 text-white px-4 py-2 rounded shadow"
          onClick={() => setToast(null)}
        >
          {toast}
        </div>
      )}
    </div>
  );
}
