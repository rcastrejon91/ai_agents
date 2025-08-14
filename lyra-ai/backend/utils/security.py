class SecurityModule:
    def __init__(self):
        self.threats = []

    def update(self, threats):
        self.threats.extend(threats)
