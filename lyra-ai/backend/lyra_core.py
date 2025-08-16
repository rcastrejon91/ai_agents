import datetime
import os

import openai
from utils.emailer import send_email
from utils.security import SecurityModule
from utils.tts import speak

openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY")


class LyraAI:
    def __init__(self, owner_name, owner_email):
        self.owner_name = owner_name
        self.owner_email = owner_email
        self.security_module = SecurityModule()
        self.self_learning_log = []
        self.current_mode = "default"

    def respond(self, message):
        # Mode detection
        if "shutdown" in message.lower():
            return "Lyra shutting down..."
        if "medical" in message.lower():
            self.current_mode = "medical"
        elif "security" in message.lower():
            self.current_mode = "security"

        # AI Chat
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": message}]
        )
        response_text = completion.choices[0].message.content
        speak(response_text)  # voice output
        self.log_learning("conversation", message)
        return response_text

    def learn_security(self):
        threats = ["Example threat X", "Example threat Y"]
        self.security_module.update(threats)
        self.log_learning("security", threats)

    def learn_medicine(self):
        studies = ["Study on cancer detection AI", "New heart surgery robotics"]
        self.log_learning("medical", studies)

    def log_learning(self, category, data):
        self.self_learning_log.append(
            {
                "timestamp": datetime.datetime.now().isoformat(),
                "category": category,
                "data": data,
            }
        )

    def email_report(self):
        send_email(self.owner_email, "Lyra Daily Report", str(self.self_learning_log))
