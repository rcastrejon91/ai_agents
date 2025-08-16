import { NextRequest, NextResponse } from "next/server";
import { update } from "../_store";

export async function POST(req: NextRequest) {
  const { device_id, autoreboot_cron } = await req.json();
  if (!device_id)
    return NextResponse.json(
      { ok: false, error: "device_id required" },
      { status: 400 },
    );
  update(device_id, { autoreboot_cron });
  return NextResponse.json({ ok: true });
}
