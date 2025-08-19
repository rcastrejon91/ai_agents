import { NextRequest, NextResponse } from "next/server";

const ROBOT_CORE_URL = process.env.ROBOT_CORE_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    
    // Validate request body
    if (typeof body.enabled !== "boolean" || !body.approval_token) {
      return NextResponse.json(
        { ok: false, error: "invalid_request" },
        { status: 400 }
      );
    }

    const response = await fetch(`${ROBOT_CORE_URL}/robot/self-repair/toggle`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Failed to toggle self-repair:", error);
    return NextResponse.json(
      { ok: false, error: "service_unavailable" },
      { status: 503 }
    );
  }
}