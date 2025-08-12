import fs from 'fs';
import path from 'path';

export type CredentialRecord = {
  credentialId: string;
  publicKey: string;
  counter: number;
  transports?: string[];
  deviceName?: string;
  addedAt: number;
};

const DATA_FILE = path.join(process.cwd(), 'server', 'admin', 'webauthn', 'credentials.json');

function load(): Record<string, CredentialRecord[]> {
  try {
    const raw = fs.readFileSync(DATA_FILE, 'utf-8');
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

function save(db: Record<string, CredentialRecord[]>): void {
  fs.mkdirSync(path.dirname(DATA_FILE), { recursive: true });
  fs.writeFileSync(DATA_FILE, JSON.stringify(db, null, 2));
}

export function listForUser(email: string): CredentialRecord[] {
  const db = load();
  return db[email] || [];
}

export function addForUser(email: string, rec: CredentialRecord): void {
  const db = load();
  const arr = db[email] || [];
  arr.push(rec);
  db[email] = arr;
  save(db);
}

export function updateCounter(email: string, credentialId: string, counter: number): void {
  const db = load();
  const arr = db[email] || [];
  const idx = arr.findIndex(r => r.credentialId === credentialId);
  if (idx >= 0) {
    arr[idx].counter = counter;
    db[email] = arr;
    save(db);
  }
}

export function removeForUser(email: string, credentialId: string): void {
  const db = load();
  db[email] = (db[email] || []).filter(r => r.credentialId !== credentialId);
  save(db);
}

const challenges: Record<string, string> = {};

export function setChallenge(email: string, challenge: string): void {
  challenges[email] = challenge;
}

export function getChallenge(email: string): string | undefined {
  return challenges[email];
}
