import wiki from 'wikipedia';
import { upsertDocWithChunks } from './ingest_utils';

function extractTitle(idOrUrl: string): string {
  try {
    const u = new URL(idOrUrl);
    const parts = u.pathname.split('/');
    return decodeURIComponent(parts[parts.length - 1]);
  } catch {
    return idOrUrl;
  }
}

export async function ingestWikipedia(idOrUrl: string) {
  const title = extractTitle(idOrUrl);
  const page = await wiki.page(title);
  const summary = await page.summary();
  const content = await page.content();
  const text = `${summary}\n\n${content}`;
  const url = `https://en.wikipedia.org/wiki/${encodeURIComponent(page.title ?? title)}`;
  return upsertDocWithChunks({ title: page.title ?? title, url, publisher: 'Wikipedia' }, text);
}

if (process.argv[1]?.includes('ingest_wikipedia')) {
  const arg = process.argv[2];
  if (!arg) {
    console.error('Usage: npm run ingest:wikipedia -- <title_or_url>');
    process.exit(1);
  }
  ingestWikipedia(arg)
    .then((r) => console.log(JSON.stringify(r)))
    .catch((e) => {
      console.error(e);
      process.exit(1);
    });
}
