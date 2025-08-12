export async function discordPost(content: string) {
  const url = process.env.DISCORD_WEBHOOK_URL!;
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  if (!r.ok) {
    console.error('Discord webhook failed', r.status, await r.text());
  }
}
