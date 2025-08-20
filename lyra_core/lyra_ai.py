from gpt4all import GPT4All
from manager import AgentManager
from lyra_core.world_state_engine import WorldStateEngine
from lyra_core.scene_soul_driver import SceneSoulDriver
from lyra_core.inner_focus_engine import InnerFocusEngine
from lyra_core.guardian_phase_two import Guardian, AstralShield


class LyraAI:
    def __init__(self, owner_name: str, owner_email: str, model="Meta-Llama-3-8B-Instruct.Q4_0.gguf"):
        self.owner_name = owner_name
        self.owner_email = owner_email
        self.llm = GPT4All(model)
        # subsystems
        self.manager = AgentManager()
        self.world = WorldStateEngine()
        self.scene = SceneSoulDriver()
        self.focus = InnerFocusEngine()
        self.guardian = Guardian()
        self.shield = AstralShield()

    def _delegate_or_answer(self, msg: str) -> str:
        # Basic router prompt — Lyra can answer or call agents
        with self.llm.chat_session():
            route = self.llm.generate(
                "You are Lyra, an orchestrator. "
                "If the user asks about stocks, reply exactly 'CALL:finance:<query>'. "
                "Legal → 'CALL:legal:<query>'. Healthcare → 'CALL:healthcare:<query>'. "
                "Retail/business ops → 'CALL:retail:<query>'. Concierge/scheduling → 'CALL:concierge:<query>'. "
                "Otherwise answer directly.\n\nUser: " + msg,
                max_tokens=120,
            ).strip()

        if route.startswith("CALL:"):
            _, agent, query = route.split(":", 2)
            return self.manager.dispatch(agent.strip(), query.strip())
        return route

    def respond(self, message: str, emotion: str = None, env=None) -> str:
        # Track inner focus + world state
        self.focus.add_focus(message, intensity=1.0, emotion=emotion)
        self.world.add_event({"type": "user_input", "text": message})
        if emotion:
            self.world.react_to_emotion(emotion)
            self.scene.match_scene_to_emotion(emotion)

        # Safety envelope (environment monitoring)
        if env:
            hazard = self.world.monitor_environment(env)
            if hazard != "Environment stable":
                return self.shield.emergency_stop() + f" ({hazard})"

        # Guardian intercept (ban words / clamp can be applied inside agents too)
        guard_check = self.guardian.scan_text(message)
        if guard_check is not None:
            return guard_check

        # Answer or delegate
        reply = self._delegate_or_answer(message)
        self.world.add_event({"type": "lyra_reply", "text": reply})
        return reply
