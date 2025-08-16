// POST /api/actions
// body: { intent: string, params?: Record<string, any> }
// returns: { status, plan?, missing?, consent?, result?, error? }

import { NextRequest, NextResponse } from "next/server";
import { planFromIntent } from "@/lib/actions/planner";
import { checkScopes, needsStrongAuth } from "@/lib/actions/policy";
import { executePlan } from "@/lib/actions/executor";

export async function POST(req: NextRequest) {
  let body: any = {};
  try {
    body = await req.json();
  } catch (err) {
    console.error("Failed to parse action request body", err);
    body = {};
  }
  const intent = String(body.intent || "").trim();
  const params = (body.params || {}) as Record<string, any>;
  if (!intent)
    return NextResponse.json(
      { status: "error", error: "missing_intent" },
      { status: 400 },
    );

  // 1) plan
  const plan = await planFromIntent(intent, params);

  // 2) scopes
  const { granted, missing } = await checkScopes(plan);
  if (missing.length) {
    return NextResponse.json({ status: "needs_scopes", plan, missing });
  }

  // 3) consent
  const needs2FA = needsStrongAuth(plan);
  const consent = {
    title: "Confirm Action",
    summary: plan.summary,
    steps: plan.steps.map((s) => ({
      id: s.id,
      kind: s.kind,
      preview: s.preview,
    })),
    requires2FA: needs2FA,
    estCostUSD: plan.estimate?.usd ?? 0,
  };
  if (!params?.confirm) {
    return NextResponse.json({ status: "needs_consent", plan, consent });
  }

  // (optional) verify TOTP/PIN if plan sensitive
  if (needs2FA) {
    const ok = await verifyTotpAndPin(params.totp, params.pin);
    if (!ok)
      return NextResponse.json(
        { status: "error", error: "auth_failed" },
        { status: 401 },
      );
  }

  // 4) execute
  const result = await executePlan(plan);
  return NextResponse.json({ status: "ok", result });
}

async function verifyTotpAndPin(t?: string, p?: string) {
  if (!t || !p) return false;
  // TODO: verify with your auth backend; stubbed true for now
  return true;
}
