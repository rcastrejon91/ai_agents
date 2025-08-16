// Twilio Programmable Voice (later): for now, simulate a call task.
export async function callStore(p: {
  phone?: string;
  script?: string;
  order?: any;
}) {
  return {
    status: "queued",
    phone: p.phone || "unknown",
    scriptPreview: (p.script || "").slice(0, 140),
  };
}
