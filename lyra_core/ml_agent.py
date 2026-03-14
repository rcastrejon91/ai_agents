import json
import os
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import pickle

class MLAgent:
    def __init__(self, name, learning_path):
        self.name = name
        self.learning_path = learning_path
        self.knowledge = self.load_learnings()
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.conversation_history = []
        self.pattern_weights = defaultdict(float)
        self.load_ml_model()
        
    def load_learnings(self):
        os.makedirs(self.learning_path, exist_ok=True)
        file_path = f"{self.learning_path}/knowledge.json"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "patterns": {},
            "responses": {},
            "context": [],
            "learned_pairs": [],
            "feedback_scores": {},
            "topic_clusters": {}
        }
    
    def save_learnings(self):
        file_path = f"{self.learning_path}/knowledge.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, indent=2)
        self.save_ml_model()
    
    def load_ml_model(self):
        model_path = f"{self.learning_path}/ml_model.pkl"
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
                self.pattern_weights = data.get('weights', defaultdict(float))
                self.conversation_history = data.get('history', [])
    
    def save_ml_model(self):
        model_path = f"{self.learning_path}/ml_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump({
                'weights': dict(self.pattern_weights),
                'history': self.conversation_history[-1000:]  # Keep last 1000
            }, f)
    
    def process_message(self, message):
        message_lower = message.lower()
        
        # Add to conversation history
        self.conversation_history.append({
            'message': message_lower,
            'timestamp': datetime.now().isoformat()
        })
        
        # Try ML-based response matching
        ml_response = self.ml_match_response(message_lower)
        if ml_response:
            learned = self.learn_pattern(message_lower, ml_response, confidence=0.9)
            return {
                "response": f"{ml_response} [ML Confidence: High]",
                "learned": learned
            }
        
        # Check learned patterns with similarity
        best_match = self.find_best_pattern_match(message_lower)
        if best_match and best_match['similarity'] > 0.7:
            response = best_match['response']
            learned = self.learn_pattern(message_lower, response, confidence=best_match['similarity'])
            return {
                "response": f"{response} [Learned Response]",
                "learned": learned
            }
        
        # Generate contextual response
        response = self.generate_response(message_lower)
        learned = self.learn_pattern(message_lower, response, confidence=0.5)
        
        return {
            "response": response,
            "learned": learned
        }
    
    def ml_match_response(self, message):
        """Use ML to find similar past conversations"""
        learned_pairs = self.knowledge.get("learned_pairs", [])
        if len(learned_pairs) < 2:
            return None
        
        try:
            # Get all past messages
            past_messages = [pair['message'] for pair in learned_pairs]
            past_responses = [pair['response'] for pair in learned_pairs]
            
            # Add current message
            all_messages = past_messages + [message]
            
            # Vectorize
            tfidf_matrix = self.vectorizer.fit_transform(all_messages)
            
            # Calculate similarity
            current_vector = tfidf_matrix[-1]
            past_vectors = tfidf_matrix[:-1]
            similarities = cosine_similarity(current_vector, past_vectors)[0]
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_similarity = similarities[best_idx]
            
            if best_similarity > 0.6:
                # Weight by feedback score
                feedback_score = self.knowledge.get("feedback_scores", {}).get(past_messages[best_idx], 1.0)
                adjusted_score = best_similarity * feedback_score
                
                if adjusted_score > 0.5:
                    return past_responses[best_idx]
        except:
            pass
        
        return None
    
    def find_best_pattern_match(self, message):
        """Find best matching learned pattern"""
        patterns = self.knowledge.get("patterns", {})
        if not patterns:
            return None
        
        best_match = None
        best_similarity = 0
        
        for pattern, data in patterns.items():
            # Simple word overlap similarity
            pattern_words = set(pattern.split())
            message_words = set(message.split())
            
            if not pattern_words or not message_words:
                continue
            
            intersection = pattern_words.intersection(message_words)
            union = pattern_words.union(message_words)
            similarity = len(intersection) / len(union) if union else 0
            
            # Weight by usage count
            count_weight = min(data.get('count', 1) / 10, 1.5)
            weighted_similarity = similarity * count_weight
            
            if weighted_similarity > best_similarity:
                best_similarity = weighted_similarity
                best_match = {
                    'pattern': pattern,
                    'response': data.get('response', ''),
                    'similarity': weighted_similarity
                }
        
        return best_match
    
    def generate_response(self, message):
        """Generate intelligent responses based on agent specialty"""
        
        # Common greetings
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"]
        if any(g in message for g in greetings):
            return f"Hello! I'm your {self.name} AI assistant powered by machine learning. How can I help you today?"
        
        # Help requests
        if "help" in message or "what can you do" in message:
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
        
        return f"[{self.name} ML Agent] I'm analyzing and learning from: '{message}'. Can you provide more context?"
    
    def wealth_response(self, message):
        keywords = {
            "invest": "Investment strategies vary based on risk tolerance. Consider diversifying across stocks, bonds, and real estate. What's your investment timeline?",
            "save": "The 50/30/20 rule: 50% needs, 30% wants, 20% savings. Are you looking for short-term or long-term strategies?",
            "stock": "Stock investing requires research. Consider index funds for diversification. What sectors interest you?",
            "crypto": "Cryptocurrency is volatile. Only invest what you can afford to lose. Bitcoin, Ethereum, or altcoins?",
            "bitcoin": "Bitcoin is the first cryptocurrency with proven long-term growth but high volatility. Research before investing.",
            "budget": "Budgeting is key to wealth building. Track expenses, set goals, automate savings. Need help creating a budget?",
            "retire": "Retirement planning should start early. Max out 401(k) matches and consider Roth IRAs. What's your timeline?",
            "debt": "Focus on high-interest debt first. Debt avalanche or snowball methods work. What type of debt?",
            "passive income": "Ideas: dividend stocks, rental properties, online courses, affiliate marketing. Which interests you?",
            "real estate": "Real estate builds wealth through appreciation and rental income. Residential or commercial?",
            "tax": "Tax planning maximizes wealth. Use tax-advantaged accounts, maximize deductions. What tax questions?"
        }
        
        for keyword, response in keywords.items():
            if keyword in message:
                self.update_pattern_weight(keyword, 1.0)
                return response
        
        return "I specialize in wealth building with ML-powered insights. What financial topic interests you?"
    
    def medical_response(self, message):
        keywords = {
            "headache": "Headaches: tension, dehydration, eye strain, migraines. Stay hydrated, rest, OTC relief. If severe/persistent, see a doctor.",
            "fever": "Monitor temperature. Rest, hydrate, fever reducers. Seek care if over 103F or lasting 3+ days.",
            "diet": "Balanced diet: fruits, vegetables, lean proteins, whole grains, healthy fats. What are your goals?",
            "nutrition": "Focus on whole foods, varied vegetables, adequate protein, hydration. What concerns?",
            "exercise": "150 minutes moderate activity weekly. Mix cardio, strength, flexibility. What's your fitness level?",
            "workout": "Effective workouts: cardio (running, cycling), strength (weights), flexibility (yoga). Your goals?",
            "sleep": "Adults need 7-9 hours. Consistent schedule, avoid screens, cool dark room. Sleep issues?",
            "insomnia": "Help: consistent schedule, relaxing routine, limit caffeine, manage stress. If chronic, see doctor.",
            "stress": "Manage through exercise, meditation, deep breathing, journaling. What stressors?",
            "anxiety": "Common condition. Try deep breathing, exercise, limit caffeine, mindfulness. If severe, seek help.",
            "depression": "Serious condition. Symptoms: persistent sadness, loss of interest, fatigue. Exercise, therapy help. Seek professional help if severe.",
            "cancer": "Complex disease with many types. Early detection key. Treatment: surgery, chemo, radiation, immunotherapy. Consult oncologist.",
            "bone cancer": "Types: osteosarcoma, chondrosarcoma, Ewing sarcoma. Symptoms: pain, swelling, fractures. Treatment: surgery, chemo, radiation.",
            "chemotherapy": "Uses drugs to kill cancer cells. Side effects: nausea, fatigue, hair loss. Oncology team guides you.",
            "infusion": "Delivers medication into bloodstream. Used for chemo, antibiotics, hydration. Done in clinic/hospital.",
            "diabetes": "Requires blood sugar management: diet, exercise, medication. Monitor regularly, balanced meals.",
            "blood pressure": "High BP increases heart disease risk. Manage: low-sodium diet, exercise, stress reduction, medication.",
            "heart": "Heart health vital. Exercise, heart-healthy foods (fish, nuts, vegetables), no smoking, manage stress.",
            "cold": "Common cold: rest, fluids, OTC meds. Resolves in 7-10 days. See doctor if worsens.",
            "flu": "Influenza: fever, body aches, fatigue. Rest, fluids, antivirals if early. Get annual flu shot.",
            "covid": "Symptoms vary. Isolate if positive, rest, hydrate. Seek care if breathing difficulty. Vaccination recommended.",
            "vitamin": "Support health. Most from diet. Common supplements: D, B12, C. Consult doctor first.",
            "weight": "Healthy management: balanced diet, exercise, sleep, stress management. Aim 1-2 lbs/week loss.",
            "pain": "Depends on cause. Options: OTC meds, physical therapy, heat/ice, rest. Chronic needs specialist.",
            "injury": "RICE: Rest, Ice, Compression, Elevation. Seek care for severe pain, swelling, inability to move.",
            "emergency": "Call 911 for: chest pain, breathing difficulty, severe bleeding, unconsciousness, stroke (FAST).",
            "machine learning": "ML in medicine: diagnosis assistance, treatment prediction, drug discovery, patient monitoring. What medical ML topic?",
            "ai diagnosis": "AI helps detect diseases from imaging, predict outcomes, personalize treatment. Not replacement for doctors."
        }
        
        for keyword, response in keywords.items():
            if keyword in message:
                self.update_pattern_weight(keyword, 1.0)
                return response
        
        return "I provide ML-enhanced health information. For specific medical concerns, consult healthcare professionals. What health topic?"
    
    def legal_response(self, message):
        keywords = {
            "contract": "Contracts: clear terms, signed by all parties, written. What type?",
            "lawsuit": "Requires evidence, proper jurisdiction. Document everything. Consult lawyer. What dispute?",
            "rights": "Rights depend on jurisdiction. Common: due process, free speech, privacy. Which rights?",
            "copyright": "Protects original works automatically. Register for full protection. What to protect?",
            "trademark": "Protects brand names/logos. Search existing, file with USPTO. What to trademark?",
            "patent": "Protects inventions. Complex, expensive. Consult patent attorney. What invention?",
            "tenant": "Rights: habitability, privacy, proper notice. What rental situation?",
            "landlord": "Must maintain conditions, follow eviction procedures, respect privacy. What problem?",
            "divorce": "Involves asset division, custody, legal dissolution. Laws vary. Consult family lawyer.",
            "custody": "Prioritizes child's best interests. Types: physical, legal, joint, sole. Document involvement.",
            "will": "Specifies asset distribution. Notarized, witnessed. Also: power of attorney, healthcare directive.",
            "estate": "Planning: wills, trusts, power of attorney, healthcare directives. Protects assets.",
            "criminal": "Involves prosecution. If charged: remain silent, get attorney immediately. What situation?",
            "arrest": "Remain calm, don't resist, don't answer without lawyer, ask for attorney. Use your rights.",
            "traffic": "Violations vary by state. Options: pay, traffic school, contest. What ticket?",
            "employment": "Covers hiring, firing, discrimination, wages, safety. Document everything. What issue?",
            "discrimination": "Illegal based on protected classes. Document, report to HR, EEOC complaint. What happened?",
            "harassment": "Workplace harassment illegal. Document, report to HR, file complaint. What type?"
        }
        
        for keyword, response in keywords.items():
            if keyword in message:
                self.update_pattern_weight(keyword, 1.0)
                return response
        
        return "I provide ML-enhanced legal information (not legal advice). Consult licensed attorney for specific matters. What legal topic?"
    
    def tech_response(self, message):
        keywords = {
            "python": "Python: great for beginners! Web dev, data science, AI, automation. Learn: variables, loops, functions. What to build?",
            "javascript": "Powers the web! Learn HTML/CSS first, then JS, then React/Vue. Your goal?",
            "react": "Popular JS library for UIs. Learn: components, props, state, hooks. Building something?",
            "html": "Structures web content. Learn: tags, attributes, semantic HTML. Pair with CSS and JS.",
            "css": "Styles web pages. Learn: selectors, box model, flexbox, grid. What design challenge?",
            "ai": "Includes ML, neural networks, NLP. Start with Python, TensorFlow/PyTorch. What AI application?",
            "machine learning": "Teaches computers to learn from data. Types: supervised, unsupervised, reinforcement. Start with Python, scikit-learn. What problem?",
            "neural network": "ML model inspired by brain. Layers of nodes process data. Used in image recognition, NLP. Want to build one?",
            "deep learning": "ML with multiple neural network layers. Powers image recognition, language models, AI. Learn: TensorFlow, PyTorch, CNNs, RNNs.",
            "nlp": "Natural Language Processing: text analysis, sentiment, translation, chatbots. Libraries: NLTK, spaCy, transformers. What NLP task?",
            "tensorflow": "Google's ML framework. Build neural networks, train models. Great for production. What are you building?",
            "pytorch": "Facebook's ML framework. Flexible, pythonic. Popular in research. What model?",
            "scikit-learn": "Python ML library. Classification, regression, clustering. Great for traditional ML. What algorithm?",
            "data science": "Extract insights from data. Skills: Python, statistics, ML, visualization. What data problem?",
            "pandas": "Python data analysis library. DataFrames for data manipulation. Essential for data science.",
            "numpy": "Python numerical computing. Arrays, math operations. Foundation for data science and ML.",
            "website": "Build with HTML, CSS, JavaScript. Frameworks: React, Vue, WordPress. What type of site?",
            "database": "Store data. SQL (MySQL, PostgreSQL) or NoSQL (MongoDB). What data?",
            "sql": "Query databases. Learn: SELECT, INSERT, UPDATE, DELETE, JOIN. What database?",
            "security": "Basics: strong passwords, 2FA, VPN, updates, backups, beware phishing. What concern?",
            "hacking": "Ethical hacking secures systems. Learn: networking, Linux, programming. Certs: CEH, OSCP.",
            "linux": "Powerful for development/servers. Start: Ubuntu, command line, file system. What use?",
            "git": "Version control. Learn: init, add, commit, push, pull, branch, merge. Essential for devs.",
            "api": "Programs communicate. REST APIs use HTTP (GET, POST, PUT, DELETE). Learn JSON, auth.",
            "cloud": "AWS, Azure, Google Cloud. Services: compute, storage, databases. What to deploy?",
            "docker": "Containers package apps with dependencies. Learn: images, containers, Dockerfile. What to containerize?",
            "blockchain": "Distributed ledger. Used in crypto, smart contracts. Learn: hashing, consensus, Solidity.",
            "algorithm": "Step-by-step problem solving. Learn: sorting, searching, dynamic programming. What algorithm?",
            "data structure": "Organize data efficiently. Learn: arrays, linked lists, trees, graphs, hash tables. What structure?"
        }
        
        for keyword, response in keywords.items():
            if keyword in message:
                self.update_pattern_weight(keyword, 1.0)
                return response
        
        return "I'm an ML-powered tech assistant. Programming, web dev, AI, databases, and more. What technology?"
    
    def get_help_message(self):
        help_texts = {
            "Wealth": "ML-Powered Wealth Agent: investing, saving, budgeting, retirement, passive income, crypto, real estate. I learn from our conversations!",
            "Medical": "ML-Powered Medical Agent: symptoms, conditions, diet, exercise, sleep, stress, wellness. I improve with each interaction! (Not medical advice)",
            "Legal": "ML-Powered Legal Agent: contracts, rights, copyright, employment, criminal law. I learn patterns from conversations! (Not legal advice)",
            "Tech": "ML-Powered Tech Agent: programming, web dev, AI/ML, data science, databases, cybersecurity, cloud. I adapt to your questions!"
        }
        return help_texts.get(self.name, f"I'm the {self.name} ML assistant. I learn and improve with every conversation!")
    
    def update_pattern_weight(self, pattern, weight):
        """Update ML pattern weights"""
        self.pattern_weights[pattern] += weight
    
    def learn_pattern(self, message, response, confidence=1.0):
        """Advanced learning with ML weighting"""
        patterns = self.knowledge.get("patterns", {})
        
        # Update pattern with confidence score
        if message in patterns:
            patterns[message]['count'] += 1
            patterns[message]['confidence'] = (patterns[message].get('confidence', 0.5) + confidence) / 2
        else:
            patterns[message] = {
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "count": 1,
                "confidence": confidence
            }
        
        self.knowledge["patterns"] = patterns
        
        # Add to learned pairs for ML training
        learned_pairs = self.knowledge.get("learned_pairs", [])
        learned_pairs.append({
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "confidence": confidence
        })
        self.knowledge["learned_pairs"] = learned_pairs[-500:]  # Keep last 500
        
        # Update context
        context = self.knowledge.get("context", [])
        context.append({
            "message": message,
            "response": response,
            "time": datetime.now().isoformat(),
            "confidence": confidence
        })
        self.knowledge["context"] = context[-100:]
        
        return {"patterns": [message], "confidence": confidence}
    
    def provide_feedback(self, message, rating):
        """Learn from user feedback (1-5 stars)"""
        feedback_scores = self.knowledge.get("feedback_scores", {})
        feedback_scores[message] = rating / 5.0  # Normalize to 0-1
        self.knowledge["feedback_scores"] = feedback_scores
        self.save_learnings()
