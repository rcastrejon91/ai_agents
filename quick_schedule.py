from time import sleep

from bots.core.launch_manager import LaunchManager, BotRegistry


reg = BotRegistry()
reg.add_bot("ping", lambda **_: print("PING!"))

mgr = LaunchManager(reg, tz="UTC")
job = mgr.schedule_launch("ping", 2)
print("Job:", job)
sleep(3)
mgr.shutdown()

