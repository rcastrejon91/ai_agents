from time import sleep
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bots.core.launch_manager import LaunchManager, BotRegistry


def test_schedule_returns_job_and_executes(tmp_path):
    ran = {"ok": False}

    def demo(target="world", **_):
        ran["ok"] = True
        return f"hi {target}"

    reg = BotRegistry()
    reg.add_bot("demo", demo)
    mgr = LaunchManager(registry=reg, tz="UTC")

    job = mgr.schedule_launch("demo", 1, target="you")
    assert job is not None

    sleep(2)  # let the job fire
    mgr.shutdown()
    assert ran["ok"] is True

