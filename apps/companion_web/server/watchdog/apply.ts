import fs from "fs";
import path from "path";
export function applyPolicy(
  jur: string,
  change: { domain: string; status: string; summary: string; sources: any[] },
) {
  const file = path.join(
    process.cwd(),
    "apps/companion_web/server/compliance/state_policies.json",
  );
  const map = JSON.parse(fs.readFileSync(file, "utf8") || "{}");
  map[jur] ||= {};
  if (change.domain === "therapy_ai") {
    map[jur]["therapy_ai"] = change.status;
    map[jur]["companion.mode"] =
      change.status === "prohibited"
        ? "journal_only"
        : change.status === "restricted"
          ? "friend+journal"
          : "friend+journal+referral";
  }
  fs.writeFileSync(file, JSON.stringify(map, null, 2));
  return map;
}
