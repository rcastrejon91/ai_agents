import type { NextApiRequest, NextApiResponse } from 'next';
import { ingestWikipedia } from '../../../../../scripts/ingest_wikipedia';
import { ingestGutenberg } from '../../../../../scripts/ingest_gutenberg';
import { ingestYouTube } from '../../../../../scripts/ingest_youtube';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { type, idOrUrl } = (req.body ?? {}) as { type?: string; idOrUrl?: string };
  if (!type || !idOrUrl) return res.status(400).json({ error: 'Missing type or idOrUrl' });

  try {
    let result;
    if (type === 'wikipedia') result = await ingestWikipedia(idOrUrl);
    else if (type === 'gutenberg') result = await ingestGutenberg(idOrUrl);
    else if (type === 'youtube') result = await ingestYouTube(idOrUrl);
    else return res.status(400).json({ error: 'Unknown type' });
    return res.status(200).json(result);
  } catch (e) {
    console.error('learn/queue error', e);
    return res.status(500).json({ error: 'ingestion failed' });
  }
}
