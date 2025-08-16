import json
import os

from fastapi import FastAPI, Request
from pydantic import BaseModel

from .repair_planner import diagnose, plan_repair
from .robot_policy import load_policy
from .safety_guard import PrimeDirective
from .telemetry_store import load_telemetry, save_telemetry

APPROVAL_TOKEN = os.getenv("REPAIR_APPROVE_TOKEN", "")
app = FastAPI(title="Lyra Robot Core", version="0.1")
guard = PrimeDirective()


class TelemetryReq(BaseModel):
    payload: dict


def _gate(action: str, ctx: dict):
    verdict = guard.evaluate(action, ctx)
    if not verdict["allow"]:
        return {"ok": False, "denied": True, "reason": verdict["reason"]}
    return {"ok": True}


@app.get("/robot/policy")
def get_policy():
    return load_policy()


@app.post("/robot/telemetry")
def post_telemetry(req: TelemetryReq):
    save_telemetry(req.payload)
    return {"ok": True}


@app.post("/robot/diagnose")
def post_diagnose():
    return diagnose(load_telemetry())


@app.post("/robot/repair/plan")
def post_plan():
    d = diagnose(load_telemetry())
    return plan_repair(d)


@app.post("/robot/repair/approve")
async def approve(request: Request):
    token = request.headers.get("x-approve-token", "")
    if token != APPROVAL_TOKEN:
        return {"ok": False, "error": "unauthorized"}
    plan = plan_repair(diagnose(load_telemetry()))
    with open("data/repair_plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    return {"ok": True, "plan_written": True}


@app.post("/robot/act/retreat")
def act_retreat(req: TelemetryReq):
    g = _gate(
        "retreat",
        {
            "lat": req.payload.get("lat"),
            "lon": req.payload.get("lon"),
            "reason": "ui_button",
        },
    )
    if not g["ok"]:
        return g
    return {"ok": True, "enqueued": "retreat"}


@app.post("/robot/act/alarm")
def act_alarm(req: TelemetryReq):
    g = _gate(
        "audible_alarm",
        {
            "lat": req.payload.get("lat"),
            "lon": req.payload.get("lon"),
            "reason": "threat_detected",
        },
    )
    if not g["ok"]:
        return g
    return {"ok": True, "enqueued": "audible_alarm"}
