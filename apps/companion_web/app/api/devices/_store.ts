import fs from 'fs';
import path from 'path';

export type Device = {
  id: string;
  public_name?: string;
  owner_email?: string;
  model?: string;
  last_seen?: number;
  autoreboot_cron?: string;
  health_url?: string;
};

const DATA_FILE = path.join(process.cwd(), 'devices.json');

function load(): Device[] {
  try {
    const raw = fs.readFileSync(DATA_FILE, 'utf8');
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

function save(devs: Device[]) {
  fs.mkdirSync(path.dirname(DATA_FILE), { recursive: true });
  fs.writeFileSync(DATA_FILE, JSON.stringify(devs, null, 2));
}

export function list(): Device[] {
  return load();
}

export function update(id: string, patch: Partial<Device>): Device {
  const devs = load();
  const idx = devs.findIndex(d => d.id === id);
  if (idx >= 0) {
    devs[idx] = { ...devs[idx], ...patch };
  } else {
    devs.push({ id, ...patch });
  }
  save(devs);
  return devs[idx >= 0 ? idx : devs.length - 1];
}

