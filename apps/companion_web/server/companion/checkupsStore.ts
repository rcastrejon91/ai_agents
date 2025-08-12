import { promises as fs } from 'fs';
import path from 'path';

export interface CheckupPrefs {
  tone: string;
  daily: boolean;
  email?: string;
  jurisdiction?: string;
}

interface StoreRecord {
  prefs: CheckupPrefs;
  messages: { text: string; timestamp: number }[];
}

const DATA_FILE = path.join(process.cwd(), 'checkupsStore.json');

async function readStore(): Promise<Record<string, StoreRecord>> {
  try {
    const data = await fs.readFile(DATA_FILE, 'utf8');
    return JSON.parse(data) as Record<string, StoreRecord>;
  } catch {
    return {};
  }
}

async function writeStore(store: Record<string, StoreRecord>): Promise<void> {
  await fs.writeFile(DATA_FILE, JSON.stringify(store, null, 2), 'utf8');
}

export async function getPrefs(userId: string): Promise<CheckupPrefs | null> {
  const store = await readStore();
  return store[userId]?.prefs || null;
}

export async function savePrefs(userId: string, prefs: CheckupPrefs): Promise<void> {
  const store = await readStore();
  const rec = store[userId] || { prefs, messages: [] };
  rec.prefs = prefs;
  store[userId] = rec;
  await writeStore(store);
}

export async function addMessage(userId: string, text: string): Promise<void> {
  const store = await readStore();
  const rec = store[userId] || { prefs: { tone: 'kind', daily: false }, messages: [] };
  rec.messages.push({ text, timestamp: Date.now() });
  store[userId] = rec;
  await writeStore(store);
}

export async function allUsers(): Promise<Record<string, StoreRecord>> {
  return await readStore();
}
