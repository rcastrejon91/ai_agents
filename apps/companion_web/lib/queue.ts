// Placeholder queue so the API shape matches a future BullMQ swap.
export type Job<T = any> = {
  id: string;
  name: string;
  data: T;
  createdAt: number;
};
const q: Job[] = [];
export async function addJob<T = any>(name: string, data: T) {
  const j: Job<T> = {
    id: Math.random().toString(36).slice(2),
    name,
    data,
    createdAt: Date.now(),
  };
  q.push(j);
  return j;
}
export function listJobs() {
  return q.slice().sort((a, b) => b.createdAt - a.createdAt);
}
