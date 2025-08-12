export const tones: Record<string, string> = {
  kind: "Just checking in—how are you feeling today?",
  playful: "Hey friend! Time for a quick self check-in.",
  professional: "Hello, this is a friendly reminder to take a moment for yourself.",
};

export const safetyFooter = "If you're in crisis, call 911 or text 988 for support.";

export function buildMessage(tone: string, mode: string): string {
  const base = tones[tone] || tones.kind;
  return `${base} [mode: ${mode}]\n\n${safetyFooter}`;
}
