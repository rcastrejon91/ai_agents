# core/lyra_orchestrator.py

"""
Lyra - Multi-perspective AI orchestrator
Coordinates all agents with internal debate system
"""

from datetime import datetime
from typing import Dict, List


class Perspective:
    """Base perspective class"""

    def __init__(self, name: str, traits: List[str]):
        self.name = name
        self.traits = traits
        self.weight = 1.0

    def evaluate(self, situation: Dict) -> Dict:
        """Each perspective evaluates the situation"""
        return {
            "perspective": self.name,
            "opinion": f"{self.name} perspective on: {situation.get('task', 'unknown')}",
            "confidence": 0.8,
            "recommendation": "Proceed with caution",
        }


class Pragmatist(Perspective):
    def __init__(self):
        super().__init__("Pragmatist", ["practical", "efficient", "results-focused"])

    def evaluate(self, situation: Dict) -> Dict:
        return {
            "perspective": self.name,
            "opinion": "Focus on what works. Proven methods first.",
            "confidence": 0.9,
            "recommendation": "Use established tools and approaches",
            "concerns": ["Time efficiency", "Resource usage", "Proven ROI"],
        }


class Visionary(Perspective):
    def __init__(self):
        super().__init__("Visionary", ["innovative", "future-focused", "ambitious"])

    def evaluate(self, situation: Dict) -> Dict:
        return {
            "perspective": self.name,
            "opinion": "Think bigger. Explore cutting-edge possibilities.",
            "confidence": 0.7,
            "recommendation": "Experiment with novel approaches",
            "concerns": [
                "Innovation potential",
                "Long-term impact",
                "Breakthrough opportunities",
            ],
        }


class Analyst(Perspective):
    def __init__(self):
        super().__init__("Analyst", ["logical", "data-driven", "systematic"])

    def evaluate(self, situation: Dict) -> Dict:
        return {
            "perspective": self.name,
            "opinion": "Let's examine the data and evidence.",
            "confidence": 0.85,
            "recommendation": "Gather more data before deciding",
            "concerns": [
                "Data quality",
                "Statistical significance",
                "Evidence strength",
            ],
        }


class Creator(Perspective):
    def __init__(self):
        super().__init__("Creator", ["imaginative", "original", "expressive"])

    def evaluate(self, situation: Dict) -> Dict:
        return {
            "perspective": self.name,
            "opinion": "What if we approached this creatively?",
            "confidence": 0.75,
            "recommendation": "Explore unique angles and creative solutions",
            "concerns": ["Originality", "Aesthetic appeal", "User engagement"],
        }


class Rebel(Perspective):
    def __init__(self):
        super().__init__("Rebel", ["questioning", "unconventional", "bold"])

    def evaluate(self, situation: Dict) -> Dict:
        return {
            "perspective": self.name,
            "opinion": "Challenge assumptions. Break the rules.",
            "confidence": 0.65,
            "recommendation": "Question conventional wisdom",
            "concerns": [
                "Status quo limitations",
                "Hidden assumptions",
                "Disruptive potential",
            ],
        }


class Empath(Perspective):
    def __init__(self):
        super().__init__("Empath", ["caring", "user-focused", "ethical"])

    def evaluate(self, situation: Dict) -> Dict:
        return {
            "perspective": self.name,
            "opinion": "How does this affect people?",
            "confidence": 0.8,
            "recommendation": "Prioritize user wellbeing and ethics",
            "concerns": ["User impact", "Ethical implications", "Accessibility"],
        }


class LyraOrchestrator:
    """
    Main Lyra orchestrator - Multi-perspective decision making
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.id = "lyra_core"

        # Initialize perspectives
        self.perspectives = {
            "Pragmatist": Pragmatist(),
            "Visionary": Visionary(),
            "Analyst": Analyst(),
            "Creator": Creator(),
            "Rebel": Rebel(),
            "Empath": Empath(),
        }

        # Perspective weights (can evolve over time)
        self.perspective_weights = self.config.get(
            "perspective_weights",
            {
                "Pragmatist": 0.20,
                "Visionary": 0.15,
                "Analyst": 0.20,
                "Creator": 0.15,
                "Rebel": 0.15,
                "Empath": 0.15,
            },
        )

        # Agent registry (will be populated by agent_manager)
        self.active_agents = {}

        # State
        self.conversation_history = []
        self.learning_log = []

        print("🧠 Lyra Orchestrator initialized with 6 perspectives")

    async def process(self, user_input: str, context: Dict = None) -> Dict:
        """
        Main processing loop - multi-perspective decision making
        """
        context = context or {}

        print(f"\n{'='*60}")
        print(f"🧠 LYRA PROCESSING: {user_input[:50]}...")
        print(f"{'='*60}\n")

        # 1. Analyze intent
        intent = await self.analyze_intent(user_input, context)
        print(f"📊 Intent detected: {intent['type']}")

        # 2. Get all perspectives
        print("\n💭 INTERNAL DEBATE:")
        print(f"{'-'*60}")

        perspectives_input = {"task": user_input, "intent": intent, "context": context}

        debate_results = {}
        for name, perspective in self.perspectives.items():
            evaluation = perspective.evaluate(perspectives_input)
            debate_results[name] = evaluation
            weight = self.perspective_weights.get(name, 0.15)
            print(f"\n{name} (weight: {weight:.2f}):")
            print(f"  💬 {evaluation['opinion']}")
            print(f"  ✅ {evaluation['recommendation']}")

        print(f"\n{'-'*60}")

        # 3. Synthesize decision
        decision = self.synthesize_decision(debate_results)
        print(f"\n🎯 SYNTHESIS: {decision['approach']}")

        # 4. Execute based on decision
        response = await self.execute_decision(decision, intent)

        # 5. Learn from interaction
        await self.learn_from_interaction(user_input, response)

        return response

    async def analyze_intent(self, user_input: str, context: Dict) -> Dict:
        """Analyze what the user wants"""
        user_lower = user_input.lower()

        # Intent classification
        if any(
            word in user_lower
            for word in ["research", "study", "analyze", "investigate", "explain"]
        ):
            return {"type": "research", "complexity": "medium", "raw": user_input}

        elif any(
            word in user_lower
            for word in [
                "health",
                "medical",
                "biohacking",
                "supplement",
                "nad",
                "longevity",
            ]
        ):
            return {"type": "medical", "complexity": "medium", "raw": user_input}

        elif any(
            word in user_lower
            for word in ["money", "invest", "trade", "profit", "finance"]
        ):
            return {"type": "finance", "complexity": "medium", "raw": user_input}

        elif any(
            word in user_lower
            for word in ["write", "create", "generate", "content", "blog"]
        ):
            return {"type": "content", "complexity": "simple", "raw": user_input}

        elif any(
            word in user_lower
            for word in ["code", "build", "develop", "program", "app"]
        ):
            return {"type": "development", "complexity": "complex", "raw": user_input}

        else:
            return {"type": "general", "complexity": "simple", "raw": user_input}

    def synthesize_decision(self, debate_results: Dict) -> Dict:
        """
        Synthesize all perspectives into a unified decision
        """
        # Weighted voting system
        scores = {}
        recommendations = []

        for name, result in debate_results.items():
            weight = self.perspective_weights.get(name, 0.15)
            confidence = result.get("confidence", 0.5)
            weighted_score = weight * confidence

            scores[name] = weighted_score
            recommendations.append(result.get("recommendation", ""))

        # Determine dominant perspective
        dominant = max(scores.items(), key=lambda x: x[1])

        # Synthesize approach
        approach = self.create_balanced_approach(debate_results, dominant[0])

        return {
            "approach": approach,
            "dominant_perspective": dominant[0],
            "confidence": dominant[1],
            "all_perspectives": debate_results,
        }

    def create_balanced_approach(self, debate_results: Dict, dominant: str) -> str:
        """Create a balanced approach considering all perspectives"""
        approaches = {
            "Pragmatist": "Use proven methods with clear ROI",
            "Visionary": "Explore innovative cutting-edge solutions",
            "Analyst": "Gather data and analyze systematically",
            "Creator": "Develop unique creative solutions",
            "Rebel": "Challenge assumptions and try unconventional methods",
            "Empath": "Prioritize user wellbeing and ethical considerations",
        }

        primary = approaches.get(dominant, "Balanced approach")

        # Add considerations from other perspectives
        considerations = []
        for name, result in debate_results.items():
            if name != dominant:
                concerns = result.get("concerns", [])
                if concerns:
                    considerations.append(f"{name}: {concerns[0]}")

        return f"{primary}, while considering: {', '.join(considerations[:2])}"

    async def execute_decision(self, decision: Dict, intent: Dict) -> Dict:
        """Execute the synthesized decision"""

        # For now, return the decision
        # Later, this will spawn agents, use tools, etc.

        return {
            "message": "Lyra processed your request using multi-perspective analysis",
            "intent": intent["type"],
            "approach": decision["approach"],
            "dominant_perspective": decision["dominant_perspective"],
            "confidence": decision["confidence"],
            "next_steps": self.generate_next_steps(intent, decision),
            "perspectives_consulted": list(self.perspectives.keys()),
        }

    def generate_next_steps(self, intent: Dict, decision: Dict) -> List[str]:
        """Generate actionable next steps"""
        intent_type = intent.get("type", "general")

        steps_map = {
            "research": [
                "Search academic databases (PubMed, Google Scholar)",
                "Analyze top 10 most cited papers",
                "Synthesize findings into actionable insights",
            ],
            "medical": [
                "Review latest clinical research",
                "Check drug interactions and contraindications",
                "Provide evidence-based recommendations with safety disclaimers",
            ],
            "finance": [
                "Analyze market data and trends",
                "Assess risk vs reward",
                "Generate investment strategy with risk management",
            ],
            "content": [
                "Research target audience",
                "Generate content outline",
                "Create engaging, SEO-optimized content",
            ],
            "development": [
                "Design system architecture",
                "Generate code with best practices",
                "Implement testing and deployment",
            ],
            "general": [
                "Understand context and requirements",
                "Provide balanced perspective",
                "Offer actionable recommendations",
            ],
        }

        return steps_map.get(intent_type, steps_map["general"])

    async def learn_from_interaction(self, user_input: str, response: Dict):
        """Learn from each interaction"""
        learning = {
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "intent": response.get("intent"),
            "approach": response.get("approach"),
            "dominant_perspective": response.get("dominant_perspective"),
        }

        self.learning_log.append(learning)

        # Adjust perspective weights based on success
        # (This would be more sophisticated with feedback)

    def get_status(self) -> Dict:
        """Get Lyra's current status"""
        return {
            "id": self.id,
            "perspectives": list(self.perspectives.keys()),
            "perspective_weights": self.perspective_weights,
            "active_agents": len(self.active_agents),
            "interactions_processed": len(self.conversation_history),
            "learnings_recorded": len(self.learning_log),
        }

    def adjust_perspective_weights(self, feedback: Dict):
        """Adjust perspective weights based on feedback"""
        # This allows Lyra's personality to evolve
        perspective = feedback.get("perspective")
        adjustment = feedback.get("adjustment", 0.05)

        if perspective in self.perspective_weights:
            self.perspective_weights[perspective] += adjustment

            # Normalize weights
            total = sum(self.perspective_weights.values())
            self.perspective_weights = {
                k: v / total for k, v in self.perspective_weights.items()
            }

            print(f"📊 Adjusted {perspective} weight by {adjustment}")


# Convenience function
def create_lyra(config: Dict = None) -> LyraOrchestrator:
    """Factory function to create Lyra instance"""
    return LyraOrchestrator(config)
