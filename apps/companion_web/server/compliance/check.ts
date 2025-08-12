import policies from "./state_policies.json";

// Returns { allowed:boolean; mode?: "journal_only"|"friend+journal"|"friend+journal+referral"; disclosure?: "strong" }
export function checkFeature(jur: string, feature: string){
  const p: any = (policies as any)[jur] || {};
  if (feature === "companion.therapy"){
    if (p.therapy_ai === "prohibited") return { allowed:false, mode:"journal_only" };
    if (p.therapy_ai === "restricted") return { allowed:true, mode:"friend+journal", disclosure:"strong" };
    return { allowed:true, mode:"friend+journal+referral" };
  }
  return { allowed:true };
}
