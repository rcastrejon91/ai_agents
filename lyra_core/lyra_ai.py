from lyra_core.guardian_phase_two import AstralShield, Guardian
from lyra_core.inner_focus_engine import InnerFocusEngine
from lyra_core.scene_soul_driver import SceneSoulDriver
from lyra_core.world_state_engine import WorldStateEngine
from manager import AgentManager


class _LLMStub:
    def chat(self, prompt: str) -> str:
        # very basic router mimic
        low = prompt.lower()
        if "stock" in low or "tesla" in low or "price" in low:
            return "CALL:finance: " + prompt
        if "law" in low or "statute" in low or "contract" in low:
            return "CALL:legal: " + prompt
        if "appointment" in low or "book" in low or "reservation" in low:
            return "CALL:concierge: " + prompt
        if "health" in low or "symptom" in low:
            return "CALL:healthcare: " + prompt
        if "retail" in low or "sku" in low:
            return "CALL:retail: " + prompt
        return "Lyra(stub): " + prompt


try:
    from gpt4all import GPT4All

    _gpt = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

    def llm_answer(msg: str) -> str:
        with _gpt.chat_session():
            return _gpt.generate(
                "You are Lyra, a router. Use CALL:<agent>:<query> when delegation fits; else answer."
                f"\nUser: {msg}",
                max_tokens=160,
            ).strip()

except Exception as _e:
    _gpt = None

    def llm_answer(msg: str) -> str:
        return _LLMStub().chat(msg)


class LyraAI:
    def __init__(self, owner_name: str, owner_email: str):
        self.owner_name = owner_name
        self.owner_email = owner_email
        self.manager = AgentManager()
        self.world = WorldStateEngine()
        self.scene = SceneSoulDriver()
        self.focus = InnerFocusEngine()
        self.guardian = Guardian()
        self.shield = AstralShield()

    def _delegate_or_answer(self, msg: str) -> str:
        route = llm_answer(msg)
        if route.startswith("CALL:"):
            _, agent, query = route.split(":", 2)
            return self.manager.dispatch(agent.strip(), query.strip())
        return route

    def respond(self, message: str, emotion: str = None, env=None) -> str:
        # inner/world/scene hooks
        self.focus.add_focus(message, 1.0, emotion)
        self.world.add_event({"type": "user_input", "text": message})
        if emotion:
            self.world.react_to_emotion(emotion)
            self.scene.match_scene_to_emotion(emotion)

        # safety: guardian text scan
        g = self.guardian.scan_text(message)
        if g:
            return g

        # safety: environment watch
        if env:
            hazard = self.world.monitor_environment(env)
            if hazard != "Environment stable":
                return self.shield.emergency_stop() + f" ({hazard})"

        reply = self._delegate_or_answer(message)
        self.world.add_event({"type": "reply", "text": reply})
        return reply
