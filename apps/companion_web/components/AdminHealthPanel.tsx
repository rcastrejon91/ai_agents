"use client";
import { useEffect, useState, useCallback } from "react";

type Robot = {
  id: string;
  type: string;
  pose: { x: number; y: number; zone: string };
  battery: number;
  status: string;
  health: { motors: string; cpu: string; tempC: number };
  lastSeen: number;
};

type SystemMetrics = {
  totalRobots: number;
  activeRobots: number;
  averageBattery: number;
  systemUptime: number;
  errorCount: number;
};

export default function AdminHealthPanel() {
  const [robots, setRobots] = useState<Robot[]>([]);
  const [log, setLog] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics>({
    totalRobots: 0,
    activeRobots: 0,
    averageBattery: 0,
    systemUptime: 0,
    errorCount: 0
  });
  const [refreshInterval, setRefreshInterval] = useState(1500);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const calculateMetrics = useCallback((robotData: Robot[]) => {
    const activeRobots = robotData.filter(r => r.status === 'active').length;
    const totalBattery = robotData.reduce((sum, r) => sum + r.battery, 0);
    const averageBattery = robotData.length > 0 ? totalBattery / robotData.length : 0;
    const errorCount = robotData.filter(r => 
      r.health.motors !== 'ok' || r.health.cpu !== 'ok' || r.health.tempC > 75
    ).length;

    setMetrics({
      totalRobots: robotData.length,
      activeRobots,
      averageBattery: Math.round(averageBattery),
      systemUptime: Date.now() - (24 * 60 * 60 * 1000), // Mock uptime
      errorCount
    });
  }, []);

  const refresh = useCallback(async () => {
    if (isRefreshing) return;
    
    setIsRefreshing(true);
    setError(null);
    
    try {
      // fetch two known robots
      const ids = ["RTU-1", "IVU-1"];
      const rs: Robot[] = [];
      
      const promises = ids.map(async (id) => {
        try {
          const response = await fetch(`/api/robots/${id}/health`);
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const j = await response.json();
          return j?.robot || null;
        } catch (err) {
          console.error(`Failed to fetch robot ${id} health:`, err);
          setLog(prev => [`Error fetching ${id}: ${err}`, ...prev].slice(0, 20));
          return null;
        }
      });

      const results = await Promise.all(promises);
      const validRobots = results.filter(Boolean);
      
      setRobots(validRobots);
      calculateMetrics(validRobots);
      
      if (validRobots.length === 0) {
        setError("No robots responding");
      }
    } catch (err) {
      console.error("Refresh failed:", err);
      setError("Failed to refresh robot data");
    } finally {
      setIsRefreshing(false);
      setIsLoading(false);
    }
  }, [isRefreshing, calculateMetrics]);

  async function dispatchRunner() {
    try {
      const r = await fetch("/api/ops/task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: "runner.deliver",
          to: "RAD-3",
          payload: { item: "lab_kit", priority: "urgent" },
        }),
      });

      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      
      const data = await r.json();
      setLog((l) =>
        [`✅ Dispatched: ${JSON.stringify(data?.task || data)}`, ...l].slice(0, 20),
      );
      refresh();
    } catch (err) {
      console.error("Dispatch failed:", err);
      setLog((l) =>
        [`❌ Dispatch failed: ${err}`, ...l].slice(0, 20),
      );
    }
  }

  async function selfTest(id: string) {
    try {
      const response = await fetch(`/api/robots/${id}/selftest`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const j = await response.json();
      setLog((l) => [`✅ Selftest ${id}: ${JSON.stringify(j)}`, ...l].slice(0, 20));
      refresh();
    } catch (err) {
      console.error("Selftest failed:", err);
      setLog((l) => [`❌ Selftest ${id} failed: ${err}`, ...l].slice(0, 20));
    }
  }

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, refreshInterval);
    return () => clearInterval(t);
  }, [refresh, refreshInterval]);

  const getBatteryColor = (battery: number) => {
    if (battery > 60) return "text-emerald-400";
    if (battery > 30) return "text-yellow-400";
    return "text-rose-400";
  };

  const getHealthStatus = (health: Robot['health']) => {
    const issues: string[] = [];
    if (health.motors !== 'ok') issues.push('motors');
    if (health.cpu !== 'ok') issues.push('cpu');
    if (health.tempC > 75) issues.push('temp');
    return issues.length === 0 ? 'healthy' : 'issues';
  };

  return (
    <div className="grid gap-4 max-w-7xl mx-auto">
      {/* Header with controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Lyra Ops Console</h2>
          {isLoading && <div className="text-sm text-zinc-400">Loading...</div>}
          {error && <div className="text-sm text-rose-400">⚠️ {error}</div>}
        </div>
        
        <div className="flex flex-wrap gap-2">
          <label className="flex items-center gap-2 text-sm">
            Refresh interval:
            <select 
              value={refreshInterval} 
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-xs"
            >
              <option value={1000}>1s</option>
              <option value={1500}>1.5s</option>
              <option value={3000}>3s</option>
              <option value={5000}>5s</option>
            </select>
          </label>
          
          <button
            onClick={refresh}
            disabled={isRefreshing}
            className="px-3 py-1 rounded bg-zinc-700 hover:bg-zinc-600 text-white text-sm disabled:opacity-50"
          >
            {isRefreshing ? "Refreshing..." : "Refresh Now"}
          </button>
          
          <button
            onClick={dispatchRunner}
            className="px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-700 text-white text-sm"
          >
            Dispatch Runner → RAD-3
          </button>
        </div>
      </div>

      {/* System Metrics Dashboard */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="card">
          <div className="text-2xl font-bold text-emerald-400">{metrics.totalRobots}</div>
          <div className="text-xs text-zinc-400">Total Robots</div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-blue-400">{metrics.activeRobots}</div>
          <div className="text-xs text-zinc-400">Active</div>
        </div>
        <div className="card">
          <div className={`text-2xl font-bold ${getBatteryColor(metrics.averageBattery)}`}>
            {metrics.averageBattery}%
          </div>
          <div className="text-xs text-zinc-400">Avg Battery</div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-purple-400">
            {Math.floor((Date.now() - metrics.systemUptime) / (1000 * 60 * 60))}h
          </div>
          <div className="text-xs text-zinc-400">Uptime</div>
        </div>
        <div className="card">
          <div className={`text-2xl font-bold ${metrics.errorCount > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
            {metrics.errorCount}
          </div>
          <div className="text-xs text-zinc-400">Errors</div>
        </div>
      </div>

      {/* Robot Status Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {robots.length === 0 && !isLoading ? (
          <div className="col-span-full text-center py-8 text-zinc-400">
            No robots available
          </div>
        ) : (
          robots.map((r) => (
            <div key={r.id} className="card hover:bg-zinc-800/50 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium">
                  {r.id} • {r.type}
                </div>
                <div className="flex items-center gap-2">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      r.status === "error" ? "bg-rose-400" : 
                      r.status === "active" ? "bg-emerald-400" : "bg-yellow-400"
                    }`}
                  />
                  <div
                    className={`text-xs ${
                      r.status === "error" ? "text-rose-400" : 
                      r.status === "active" ? "text-emerald-400" : "text-yellow-400"
                    }`}
                  >
                    {r.status}
                  </div>
                </div>
              </div>
              
              <div className="text-sm text-zinc-400 space-y-1">
                <div>
                  Zone <span className="text-zinc-300 font-medium">{r.pose.zone}</span> • 
                  Position ({r.pose.x.toFixed(1)}, {r.pose.y.toFixed(1)})
                </div>
                <div>
                  Battery <span className={`font-medium ${getBatteryColor(r.battery)}`}>
                    {r.battery.toFixed(0)}%
                  </span> • 
                  Temp <span className={`font-medium ${r.health.tempC > 75 ? 'text-rose-400' : 'text-zinc-300'}`}>
                    {r.health.tempC.toFixed(1)}°C
                  </span>
                </div>
                <div>
                  Health: Motors <span className={`text-xs ${r.health.motors === 'ok' ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {r.health.motors}
                  </span>, CPU <span className={`text-xs ${r.health.cpu === 'ok' ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {r.health.cpu}
                  </span>
                </div>
                <div className="text-xs">
                  Last seen: {new Date(r.lastSeen).toLocaleTimeString()}
                </div>
              </div>
              
              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  onClick={() => selfTest(r.id)}
                  className="px-2 py-1 rounded border border-zinc-700 hover:border-zinc-600 text-xs transition-colors"
                >
                  Self-test
                </button>
                <button
                  onClick={() =>
                    fetch(`/api/robots/${r.id}/command`, {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        cmd: "goto",
                        args: { waypoint: "LOBBY" },
                      }),
                    }).then(() => {
                      setLog(l => [`📍 ${r.id} moving to LOBBY`, ...l].slice(0, 20));
                    }).catch(err => {
                      setLog(l => [`❌ Failed to send ${r.id} to LOBBY: ${err}`, ...l].slice(0, 20));
                    })
                  }
                  className="px-2 py-1 rounded border border-zinc-700 hover:border-zinc-600 text-xs transition-colors"
                >
                  Send → LOBBY
                </button>
                <button
                  onClick={() =>
                    fetch(`/api/robots/${r.id}/command`, {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        cmd: "emergency_stop",
                      }),
                    }).then(() => {
                      setLog(l => [`🛑 Emergency stop: ${r.id}`, ...l].slice(0, 20));
                    }).catch(err => {
                      setLog(l => [`❌ Failed to stop ${r.id}: ${err}`, ...l].slice(0, 20));
                    })
                  }
                  className="px-2 py-1 rounded border border-rose-700 hover:border-rose-600 text-xs text-rose-400 transition-colors"
                >
                  🛑 Stop
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Event Log */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-zinc-400">Event Log</div>
          <button
            onClick={() => setLog([])}
            className="text-xs text-zinc-500 hover:text-zinc-400"
          >
            Clear
          </button>
        </div>
        <div className="max-h-44 overflow-auto">
          {log.length === 0 ? (
            <div className="text-xs text-zinc-500 italic">No events</div>
          ) : (
            <ul className="text-xs space-y-1">
              {log.map((line, i) => (
                <li key={i} className="text-zinc-400 font-mono">
                  <span className="text-zinc-500">{new Date().toLocaleTimeString()}</span> {line}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
