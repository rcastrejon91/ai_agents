import fetch from 'cross-fetch';
import { YoutubeTranscript } from 'youtube-transcript';
import { upsertDocWithChunks } from './ingest_utils';

function getVideoId(url: string): string {
  try {
    const u = new URL(url);
    if (u.hostname === 'youtu.be') return u.pathname.slice(1);
    return u.searchParams.get('v') || '';
  } catch {
    return url;
  }
}

export async function ingestYouTube(url: string) {
  const videoId = getVideoId(url);
  const transcript = await YoutubeTranscript.fetchTranscript(videoId);
  const text = transcript.map((t) => t.text).join(' ');
  const meta = await fetch(
    `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`
  )
    .then((r) => r.json())
    .catch(() => null);
  const title = meta?.title || `YouTube Video ${videoId}`;
  const channel = meta?.author_name;
  const published_at = meta?.upload_date;
  return upsertDocWithChunks(
    {
      title,
      url,
      publisher: 'YouTube',
      metadata: { video_id: videoId, channel, published_at },
    },
    text
  );
}

if (process.argv[1]?.includes('ingest_youtube')) {
  const arg = process.argv[2];
  if (!arg) {
    console.error('Usage: npm run ingest:youtube -- <url>');
    process.exit(1);
  }
  ingestYouTube(arg)
    .then((r) => console.log(JSON.stringify(r)))
    .catch((e) => {
      console.error(e);
      process.exit(1);
    });
}
