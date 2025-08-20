from lyra_core.lyra_ai import LyraAI

if __name__ == "__main__":
    lyra = LyraAI("Ricky", "ricardomcastrejon@gmail.com")
    print("Lyra online. Type 'quit' to exit.\n")
    while True:
        msg = input("You: ")
        if msg.lower() in ("quit", "exit"):
            break
        ans = lyra.respond(msg, emotion=None, env={"obstacle_distance": 2.0, "temp_c": 24})
        print("Lyra:", ans)
