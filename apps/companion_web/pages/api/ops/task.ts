import type { NextApiRequest, NextApiResponse } from "next";
import { addJob } from "../../../lib/queue";
import { scheduleTask, Task } from "../../../lib/robots";

export default async function handler(req:NextApiRequest, res:NextApiResponse) {
  if (req.method !== "POST") return res.status(405).json({ error:"Method not allowed" });
  try {
    const { type, to, payload } = req.body || {};
    if (!type || !to) return res.status(400).json({ error:"type and to required" });
    const job = await addJob("ops.task", { type, to, payload });

    const task: Task = {
      id: "tsk_" + job.id,
      type,
      to,
      payload,
      status: "queued",
      createdAt: Date.now(),
    };
    const assigned = scheduleTask(task);
    return res.status(200).json({ ok:true, task: assigned });
  } catch (e:any) {
    console.error(e);
    return res.status(500).json({ error:"server" });
  }
}
