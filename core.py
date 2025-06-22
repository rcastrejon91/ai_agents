class WraithForgeCore:
    def __init__(self):
        self.modules = {}
        self.active = False

    def activate(self):
        self.active = True
        print("🗡️ WraithForge AI online. Ready to engage offensive protocols.")

    def load_module(self, name, function):
        self.modules[name] = function
        print(f"⚙️ Module '{name}' loaded.")

    def run_module(self, name, *args):
        if name in self.modules:
            return self.modules[name](*args)
        else:
            return "❌ Module not found."
