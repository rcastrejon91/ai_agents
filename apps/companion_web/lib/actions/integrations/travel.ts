export async function searchTravel(p: { from: string; to: string; start: string; days: number }) {
  // Start with an affiliate or deep-link search; upgrade later to Amadeus/Booking APIs.
  return { status: 'ok', search: `Flights ${p.from} ⇄ ${p.to} around ${p.start} for ${p.days} days` };
}
export async function bookTravel(p: { hold: boolean }) {
  return { status: p.hold ? 'held' : 'booked', reference: `TRIP-${Date.now()}` };
}
