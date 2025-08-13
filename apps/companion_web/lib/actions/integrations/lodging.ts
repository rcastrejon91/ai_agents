export async function searchLodging(p: { city: string; guests: number; start: string; days: number }) {
  return { status: 'ok', search: `Lodging in ${p.city} for ${p.guests}, ${p.start} +${p.days} nights` };
}
export async function requestLodging(p: { platform: 'preferred' | 'airbnb' | 'vrbo'; hold: boolean }) {
  return { status: 'requested', platform: p.platform || 'preferred', ref: `LODGE-${Date.now()}` };
}
