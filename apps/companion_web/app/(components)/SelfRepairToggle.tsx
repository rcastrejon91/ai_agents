"use client";
import { useEffect, useState } from "react";

type SelfRepairState = {
  self_repair_enabled: boolean;
  approve_required: boolean;
};

export default function SelfRepairToggle() {
  const [state, setState] = useState<SelfRepairState | null>(null);
  const [approvalToken, setApprovalToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>("");

  async function loadStatus() {
    try {
      const r = await fetch("/api/robot/self-repair/status");
      const data = await r.json();
      if (data.ok) {
        setState({
          self_repair_enabled: data.self_repair_enabled,
          approve_required: data.approve_required,
        });
      }
    } catch (err) {
      console.error("Failed to load self-repair status", err);
    }
  }

  useEffect(() => {
    loadStatus();
    // Refresh status every 30 seconds
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  async function toggleSelfRepair(enabled: boolean) {
    if (!approvalToken.trim()) {
      alert("Please enter approval token");
      return;
    }

    setLoading(true);
    try {
      const r = await fetch("/api/robot/self-repair/toggle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          enabled,
          approval_token: approvalToken,
        }),
      });
      
      const data = await r.json();
      if (data.ok) {
        setState({
          self_repair_enabled: data.self_repair_enabled,
          approve_required: data.approve_required,
        });
        setLastUpdate(new Date().toLocaleTimeString());
        setApprovalToken(""); // Clear token after use
      } else {
        alert(`Failed to update setting: ${data.error}`);
      }
    } catch (err) {
      console.error("Failed to toggle self-repair", err);
      alert("Network error occurred");
    } finally {
      setLoading(false);
    }
  }

  if (!state) return <div className="text-sm text-zinc-500">Loading self-repair status...</div>;

  return (
    <div className="rounded border border-zinc-800 p-3">
      <div className="mb-2 text-sm">
        <div className="flex items-center justify-between">
          <span>Self-Repair Mode:</span>
          <span className={`font-bold ${state.self_repair_enabled ? "text-orange-400" : "text-emerald-400"}`}>
            {state.self_repair_enabled ? "ENABLED" : "DISABLED"}
          </span>
        </div>
        <div className="text-xs text-zinc-500 mt-1">
          Human Approval: <span className="text-emerald-400 font-medium">REQUIRED</span>
          {lastUpdate && <span className="ml-2">• Updated: {lastUpdate}</span>}
        </div>
      </div>

      <input
        className="w-full px-2 py-1 rounded border border-zinc-700 bg-zinc-900 text-sm mb-2"
        placeholder="Enter Approval Token"
        type="password"
        value={approvalToken}
        onChange={(e) => setApprovalToken(e.target.value)}
        disabled={loading}
      />

      <div className="flex gap-2">
        <button
          className={`px-3 py-1 rounded text-sm transition-colors ${
            state.self_repair_enabled
              ? "bg-zinc-700 text-zinc-400 cursor-not-allowed"
              : "bg-emerald-600 hover:bg-emerald-700 text-white"
          }`}
          onClick={() => toggleSelfRepair(true)}
          disabled={loading || state.self_repair_enabled}
        >
          {loading ? "..." : "Enable"}
        </button>
        <button
          className={`px-3 py-1 rounded text-sm transition-colors ${
            !state.self_repair_enabled
              ? "bg-zinc-700 text-zinc-400 cursor-not-allowed"
              : "bg-red-600 hover:bg-red-700 text-white"
          }`}
          onClick={() => toggleSelfRepair(false)}
          disabled={loading || !state.self_repair_enabled}
        >
          {loading ? "..." : "Disable"}
        </button>
      </div>

      <div className="mt-2 text-xs text-zinc-500">
        ⚠️ Self-repair allows the robot to attempt automatic hardware/software fixes.
        Human approval is always required before any repair action is executed.
      </div>
    </div>
  );
}