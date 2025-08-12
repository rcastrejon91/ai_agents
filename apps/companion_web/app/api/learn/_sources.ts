export const RSS_FEEDS = [
  'https://hnrss.org/frontpage',
  'https://arxiv.org/rss/cs.AI',
  'https://blog.google/rss',
  'https://openai.com/blog/rss.xml'
];

export function allowedDomain(url: string) {
  const allow = (process.env.LEARN_ALLOWED_DOMAINS || '')
    .split(',').map(s => s.trim()).filter(Boolean);
  try {
    const u = new URL(url);
    return allow.length ? allow.some(d => u.hostname.endsWith(d)) : true;
  } catch {
    return false;
  }
}
