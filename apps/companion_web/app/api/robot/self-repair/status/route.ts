import { NextRequest, NextResponse } from "next/server";

const ROBOT_CORE_URL = process.env.ROBOT_CORE_URL || "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${ROBOT_CORE_URL}/robot/self-repair/status`);
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to fetch self-repair status:", error);
    return NextResponse.json(
      { ok: false, error: "service_unavailable" },
      { status: 503 }
    );
  }
}