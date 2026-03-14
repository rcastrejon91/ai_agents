import json
import os
from datetime import datetime

class SmartAgent:
    def __init__(self, name, learning_path):
        self.name = name
        self.learning_path = learning_path
        self.knowledge = self.load_learnings()
        
    def load_learnings(self):
        os.makedirs(self.learning_path, exist_ok=True)
        file_path = f"{self.learning_path}/knowledge.json"
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {"patterns": {}, "responses": {}, "context": []}
    
    def save_learnings(self):
        file_path = f"{self.learning_path}/knowledge.json"
        with open(file_path, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def process_message(self, message):
        message_lower = message.lower()
        
        # Check for patterns in knowledge base
        for pattern, response in self.knowledge.get("responses", {}).items():
            if pattern in message_lower:
                return {
                    "response": response,
                    "learned": {"patterns": []}
                }
        
        # Generate contextual response based on agent type
        response = self.generate_response(message_lower)
        
        # Learn from this interaction
        learned = self.learn_pattern(message_lower, response)
        
        return {
            "response": response,
            "learned": learned
        }
    
    def generate_response(self, message):
        """Generate intelligent responses based on agent specialty"""
        
        # Common greetings
        greetings = ["hello", "hi", "hey", "greetings"]
        if any(g in message for g in greetings):
            return f"Hello! I'm your {self.name} AI assistant. How can I help you today?"
        
        # Help requests
        if "help" in message:
            return self.get_help_message()
        
        # Agent-specific responses
        if self.name == "Wealth":
            return self.wealth_response(message)
        elif self.name == "Medical":
            return self.medical_response(message)
        elif self.name == "Legal":
            return self.legal_response(message)
        elif self.name == "Tech":
            return self.tech_response(message)
        
        return f"[{self.name}] I'm learning about: '{message}'. Can you tell me more?"
    
    def wealth_response(self, message):
        keywords = {
            "invest": "Investment strategies vary based on risk tolerance. Consider diversifying across stocks, bonds, and real estate. What's your investment timeline?",
            "save": "Great question! The 50/30/20 rule is popular: 50% needs, 30% wants, 20% savings. Are you looking for short-term or long-term savings strategies?",
            "stock": "Stock investing requires research. Consider index funds for diversification. What sectors interest you?",
            "crypto": "Cryptocurrency is volatile. Only invest what you can afford to lose. Are you interested in Bitcoin, Ethereum, or altcoins?",
            "budget": "Budgeting is key to wealth building. Track expenses, set goals, and automate savings. Need help creating a budget?",
            "retire": "Retirement planning should start early. Max out 401(k) matches and consider Roth IRAs. What's your retirement timeline?",
            "debt": "Focus on high-interest debt first. Consider debt avalanche or snowball methods. What type of debt are you managing?",
            "passive income": "Passive income ideas: dividend stocks, rental properties, online courses, or affiliate marketing. Which interests you?"
        }
        
        for keyword, response in keywords.items():
            if keyword in message:
                return response
        
        return "I specialize in wealth building, investing, budgeting, and financial freedom. What financial topic can I help you with?"
    
    def medical_response(self, message):
        keywords = {
            "headache": "Headaches can have many causes. Stay hydrated, rest, and consider over-the-counter pain relief. If persistent, consult a doctor.",
            "fever": "Monitor your temperature. Rest, stay hydrated, and use fever reducers if needed. Seek medical attention if over 103F or lasting 3+ days.",
            "diet": "A balanced diet includes fruits, vegetables, lean proteins, and whole grains. What are your dietary goals?",
            "exercise": "Aim for 150 minutes of moderate activity weekly. Mix cardio and strength training. What's your fitness level?",
            "sleep": "Adults need 7-9 hours of sleep. Maintain a consistent schedule and create a relaxing bedtime routine.",
            "stress": "Manage stress through exercise, meditation, deep breathing, or talking to someone. What stressors are you facing?"
        }
        
        for keyword, response in keywords.items():
            if keyword in message:
                return response
        
        return "I provide general health information. For specific medical concerns, please consult a healthcare professional. What health topic interests you?"
    
    def legal_response(self, message):
        keywords = {
            "contract": "Contracts should be clear, signed by all parties, and include terms, conditions, and consequences. What type of contract?",
            "lawsuit": "Legal action requires evidence and proper jurisdiction. Consult a lawyer for your specific case. What's the dispute about?",
            "rights": "Your rights depend on jurisdiction and situation. What specific rights are you asking about?",
            "copyright": "Copyright protects original works. Register with the Copyright Office for full protection. What are you trying to protect?",
            "tenant": "Tenant rights vary by location but typically include habitability and privacy. What's your rental situation?"
        }
        
        for keyword, response in keywords.items():
            if keyword in message:
                return response
        
        return "I provide general legal information (not legal advice). For specific legal matters, consult a licensed attorney. What legal topic can I help explain?"
    
    def tech_response(self, message):
        keywords = {
            "python": "Python is great for beginners! It's used in web dev, data science, AI, and automation. What do you want to build?",
            "javascript": "JavaScript powers the web! Learn HTML/CSS first, then JS frameworks like React or Vue. What's your goal?",
            "ai": "AI includes machine learning, neural networks, and NLP. Start with Python and TensorFlow. What AI application interests you?",
            "website": "Build websites with HTML, CSS, JavaScript. Use frameworks like React or WordPress. What type of site?",
            "database": "Databases store data. SQL for relational (MySQL, PostgreSQL) or NoSQL (MongoDB). What data are you managing?",
            "security": "Cybersecurity basics: strong passwords, 2FA, VPN, regular updates. What security concern do you have?"
        }
        
        for keyword, response in keywords.items():
            if keyword in message:
                return response
        
        return "I can help with programming, web development, AI, databases, and tech topics. What technology interests you?"
    
    def get_help_message(self):
        help_texts = {
            "Wealth": "I can help with: investing, saving, budgeting, retirement planning, passive income, debt management, and wealth building strategies.",
            "Medical": "I provide general health info on: symptoms, diet, exercise, sleep, stress management, and wellness tips. (Not a substitute for professional medical advice)",
            "Legal": "I explain legal concepts like: contracts, rights, copyright, tenant law, and legal processes. (Not legal advice - consult an attorney for specific cases)",
            "Tech": "I assist with: programming, web development, AI/ML, databases, cybersecurity, and technology questions."
        }
        return help_texts.get(self.name, f"I'm the {self.name} assistant. Ask me anything!")
    
    def learn_pattern(self, message, response):
        """Store learned patterns"""
        patterns = self.knowledge.get("patterns", {})
        patterns[message] = {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "count": patterns.get(message, {}).get("count", 0) + 1
        }
        self.knowledge["patterns"] = patterns
        
        # Add to context
        context = self.knowledge.get("context", [])
        context.append({"message": message, "response": response, "time": datetime.now().isoformat()})
        self.knowledge["context"] = context[-100:]  # Keep last 100 interactions
        
        return {"patterns": [message]}
