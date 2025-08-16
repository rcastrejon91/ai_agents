// Start with universal deep link (user taps to open the app)
// Later: swap to provider APIs once tokens added.
export async function requestRideDeepLink(p: {
  pickup: string;
  dropoff: string;
  service: string;
}) {
  const u = new URL("https://m.uber.com/ul/"); // generic deeplink
  if (p.dropoff && typeof p.dropoff === "string")
    u.searchParams.set("action", "setPickup");
  // NOTE: You should map real lat/lon when available. For now, fallback strings.
  return {
    type: "deeplink",
    url: u.toString(),
    note: "Tap to request in your ride app.",
  };
}
