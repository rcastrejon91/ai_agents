// Simple in-memory robot fleet + simulator loop.
// Safe for demos: NO real hardware calls, NO PHI.

export type RobotType = "runner" | "iv" | "surgical";
export type Robot = {
  id: string;
  type: RobotType;
  pose: { x: number; y: number; zone: string };
  battery: number; // 0..100
  status: "idle" | "moving" | "busy" | "error";
  health: {
    motors: "ok" | "warn" | "fail";
    cpu: "ok" | "warn" | "fail";
    tempC: number;
  };
  lastSeen: number;
  taskId?: string;
};

export type Task = {
  id: string;
  type: "runner.deliver" | "iv.start";
  to: string; // waypoint/room
  payload?: Record<string, any>; // { item: "lab_kit" }
  status: "queued" | "assigned" | "done" | "error";
  robotId?: string;
  createdAt: number;
  finishedAt?: number;
};

const robots: Record<string, Robot> = {
  "RTU-1": {
    id: "RTU-1",
    type: "runner",
    pose: { x: 0, y: 0, zone: "LOBBY" },
    battery: 96,
    status: "idle",
    health: { motors: "ok", cpu: "ok", tempC: 41 },
    lastSeen: Date.now(),
  },
  "IVU-1": {
    id: "IVU-1",
    type: "iv",
    pose: { x: 3, y: 1, zone: "ER" },
    battery: 88,
    status: "idle",
    health: { motors: "ok", cpu: "ok", tempC: 39 },
    lastSeen: Date.now(),
  },
};

const tasks: Record<string, Task> = {};
const waypoints: Record<string, { x: number; y: number; zone: string }> = {
  LOBBY: { x: 0, y: 0, zone: "LOBBY" },
  ER: { x: 3, y: 1, zone: "ER" },
  "RAD-3": { x: 8, y: 2, zone: "RAD" },
  "OR-2": { x: 5, y: 7, zone: "OR" },
  LAB: { x: 2, y: 6, zone: "LAB" },
};

function rnd(n: number) {
  return Math.random() * n;
}
function clamp(v: number, min: number, max: number) {
  return Math.max(min, Math.min(max, v));
}

function tickRobot(r: Robot) {
  // battery drain + temp wiggle
  r.battery = clamp(r.battery - (r.status === "moving" ? 0.06 : 0.02), 5, 100);
  r.health.tempC = clamp(r.health.tempC + (Math.random() - 0.5) * 0.8, 35, 70);
  r.lastSeen = Date.now();

  // simple failure sim
  if (r.health.tempC > 65 && Math.random() < 0.02) {
    r.status = "error";
    r.health.motors = "warn";
    return;
  }

  // "moving" -> drift toward target coords encoded in pose.zone (waypoint)
  const wp = waypoints[r.pose.zone];
  if (!wp) return;

  // drift to wp coords
  if (r.status === "moving") {
    const dx = wp.x - r.pose.x;
    const dy = wp.y - r.pose.y;
    const step = 0.35;
    const dist = Math.hypot(dx, dy);
    if (dist < 0.4) {
      r.status = "busy"; // arrived, "doing task"
      setTimeout(
        () => {
          r.status = "idle";
          if (r.taskId && tasks[r.taskId]) {
            tasks[r.taskId].status = "done";
            tasks[r.taskId].finishedAt = Date.now();
          }
          r.taskId = undefined;
        },
        1000 + rnd(1200),
      );
    } else {
      r.pose.x += (dx / dist) * step + (Math.random() - 0.5) * 0.05;
      r.pose.y += (dy / dist) * step + (Math.random() - 0.5) * 0.05;
    }
  }
}

setInterval(() => {
  Object.values(robots).forEach(tickRobot);
}, 400);

// PUBLIC API
export function listRobots(): Robot[] {
  return Object.values(robots);
}
export function getRobot(id: string) {
  return robots[id];
}
export function setWaypoint(name: string, x: number, y: number, zone: string) {
  waypoints[name] = { x, y, zone };
}

export function goto(
  id: string,
  waypoint: string,
): { accepted: boolean; eta_s: number } {
  const r = robots[id];
  const wp = waypoints[waypoint];
  if (!r || !wp) return { accepted: false, eta_s: 0 };
  r.pose.zone = waypoint;
  r.status = "moving";
  const eta = Math.round(Math.hypot(wp.x - r.pose.x, wp.y - r.pose.y) / 0.35);
  return { accepted: true, eta_s: eta };
}

export function scheduleTask(task: Task) {
  tasks[task.id] = task;
  // naive assign to first idle runner
  const runner = Object.values(robots).find(
    (r) => r.type === "runner" && r.status === "idle",
  );
  if (runner) {
    task.status = "assigned";
    task.robotId = runner.id;
    runner.taskId = task.id;
    goto(runner.id, task.to);
  }
  return task;
}

export function getTasks() {
  return Object.values(tasks).sort((a, b) => b.createdAt - a.createdAt);
}
