// scripts/check-pages-default-export.mjs
import fs from "node:fs";
import path from "node:path";

const targetDir = process.argv[2] || "apps/companion_web/pages";

// Basic heuristics for a default export in a React page
const hasDefaultExport = (src) =>
  /export\s+default\s+function\s+[A-Za-z0-9_]+/.test(src) || // export default function Page() {}
  /export\s+default\s+\(?.*=>/.test(src) || // export default () => ... / const Page = () => ...; export default Page
  /export\s+\{\s*default\s+as\s+[A-Za-z0-9_]+\s*\}\s+from/.test(src) || // re-export default
  /module\.exports\s*=/.test(src); // JS fallback

function walk(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (
        p.includes(`${path.sep}api${path.sep}`) ||
        p.endsWith(`${path.sep}api`)
      ) {
        continue;
      } // skip API routes
      walk(p);
    } else if (/\.(tsx?|jsx?)$/.test(e.name)) {
      // Ignore type-only or non-page helpers by convention
      if (e.name.endsWith(".d.ts")) {
        continue;
      }

      const src = fs.readFileSync(p, "utf8");
      const isPage = !p.includes(`${path.sep}api${path.sep}`);

      if (isPage && !hasDefaultExport(src)) {
        console.log("❌ Missing default export:", p);
      }
    }
  }
}

if (!fs.existsSync(targetDir)) {
  console.error("Path not found:", targetDir);
  process.exit(1);
}

console.log("Scanning pages for default exports in:", targetDir);
walk(targetDir);
console.log("✅ Scan complete.");
