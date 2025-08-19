import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const pagesDir = path.join(__dirname, "..", "pages");

const missing = [];

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full);
    } else if (/\.(t|j)sx?$/.test(entry.name)) {
      if (entry.name.startsWith("_") || entry.name.endsWith(".d.ts")) {
        continue;
      }
      const content = fs.readFileSync(full, "utf8");
      if (!/export\s+default/.test(content)) {
        missing.push(path.relative(pagesDir, full));
      }
    }
  }
}

walk(pagesDir);

if (missing.length) {
  console.error("Missing default export in the following pages:");
  for (const m of missing) {
    console.error(" - " + m);
  }
  process.exit(1);
} else {
  console.log("All pages have a default export.");
}
