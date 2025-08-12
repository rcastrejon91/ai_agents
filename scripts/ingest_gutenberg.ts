import fetch from 'cross-fetch';
import { upsertDocWithChunks } from './ingest_utils';

function buildUrl(idOrUrl: string): string {
  if (/^https?:\/\//.test(idOrUrl)) return idOrUrl;
  const id = idOrUrl.replace(/[^0-9]/g, '');
  return `https://www.gutenberg.org/cache/epub/${id}/pg${id}.txt`;
}

function stripGutenberg(text: string): string {
  return text
    .replace(/[\s\S]*\*\*\* START OF THE PROJECT GUTENBERG[^]*?\*\*\*\n/, '')
    .replace(/\*\*\* END OF THE PROJECT GUTENBERG[\s\S]*/, '')
    .trim();
}

export async function ingestGutenberg(idOrUrl: string) {
  const url = buildUrl(idOrUrl);
  const res = await fetch(url);
  const raw = await res.text();
  const text = stripGutenberg(raw);
  const title = text.split('\n')[0].trim();
  return upsertDocWithChunks(
    { title: title || `Gutenberg ${idOrUrl}`, url, publisher: 'Project Gutenberg', license: 'Public Domain' },
    text
  );
}

if (process.argv[1]?.includes('ingest_gutenberg')) {
  const arg = process.argv[2];
  if (!arg) {
    console.error('Usage: npm run ingest:gutenberg -- <id_or_url>');
    process.exit(1);
  }
  ingestGutenberg(arg)
    .then((r) => console.log(JSON.stringify(r)))
    .catch((e) => {
      console.error(e);
      process.exit(1);
    });
}
