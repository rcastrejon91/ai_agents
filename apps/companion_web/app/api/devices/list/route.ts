import { NextResponse } from "next/server";
import { list } from "../_store";

export const dynamic = "force-dynamic";

export async function GET() {
  const devices = list();
  return NextResponse.json({ devices });
}
