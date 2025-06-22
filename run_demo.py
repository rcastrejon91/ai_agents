from core import WraithForgeCore
from modules.fire import pyro_pulse
from modules.ice import cryo_breach
from modules.mind import neuro_disturb
from modules.amplify import amplify_spell

# Optional: Amplify spells
pyro_pulse = amplify_spell(pyro_pulse)
cryo_breach = amplify_spell(cryo_breach)

wf = WraithForgeCore()
wf.activate()

wf.load_module("fire", pyro_pulse)
wf.load_module("ice", cryo_breach)
wf.load_module("mind", neuro_disturb)

print(wf.run_module("fire", "Shadow Entity"))
print(wf.run_module("ice", "Hostile Area"))
print(wf.run_module("mind", "Enemy AI"))
