import type { NextApiRequest, NextApiResponse } from "next";

type Lab = { code: string; value: number; unit?: string; sex?: "M" | "F" };
type Flag = { code: string; flag: "low" | "high" | "critical"; note: string };

// very basic, demo-only reference ranges (adults)
const ranges: Record<
  string,
  { low: number; high: number; unit?: string; note: string }
> = {
  HGB_F: {
    low: 12.0,
    high: 16.0,
    unit: "g/dL",
    note: "Hemoglobin (female typical range)",
  },
  HGB_M: {
    low: 13.5,
    high: 17.5,
    unit: "g/dL",
    note: "Hemoglobin (male typical range)",
  },
  WBC: { low: 4.0, high: 11.0, unit: "x10^3/µL", note: "White blood cells" },
  PLT: { low: 150, high: 450, unit: "x10^3/µL", note: "Platelets" },
  GLU: { low: 70, high: 99, unit: "mg/dL", note: "Fasting glucose (may vary)" },
};

function evalLab(l: Lab): Flag | null {
  if (l.code === "HGB") {
    const key = l.sex === "M" ? "HGB_M" : "HGB_F";
    const r = ranges[key];
    if (!r) return null;
    if (l.value < r.low)
      return {
        code: "HGB",
        flag: "low",
        note: `Below typical range. ${r.note}`,
      };
    if (l.value > r.high)
      return {
        code: "HGB",
        flag: "high",
        note: `Above typical range. ${r.note}`,
      };
    return null;
  }
  const r = ranges[l.code];
  if (!r) return null;
  if (l.value < r.low)
    return {
      code: l.code,
      flag: "low",
      note: `Below typical range. ${r.note}`,
    };
  if (l.value > r.high)
    return {
      code: l.code,
      flag: "high",
      note: `Above typical range. ${r.note}`,
    };
  return null;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST")
    return res.status(405).json({ error: "Method not allowed" });
  const { panel = [] } = req.body || {};
  const flags = (panel as Lab[]).map(evalLab).filter(Boolean) as Flag[];
  const education =
    "These ranges are generalized and for education only. Lab interpretation depends on context. " +
    "For urgent concerns or symptoms, seek clinician care or emergency services.";
  return res
    .status(200)
    .json({ flags, education, disclaimer: "Not medical advice." });
}
