import type { NextApiRequest } from "next";
export function resolveJurisdiction(req: NextApiRequest, fallback="US-FED"){
  // Priority: explicit header → cookie → fallback
  const h = (req.headers["x-jurisdiction"] || "").toString().trim();
  if (h) return h;
  const cookie = (req.headers.cookie || "").split(";").map(s=>s.trim()).find(s=>s.startsWith("jurisdiction="));
  if (cookie) return decodeURIComponent(cookie.split("=")[1]);
  return fallback;
}
