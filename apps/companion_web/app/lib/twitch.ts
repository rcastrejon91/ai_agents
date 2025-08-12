export async function twitchTokenFromCode(code: string) {
  const url = new URL('https://id.twitch.tv/oauth2/token');
  url.searchParams.set('client_id', process.env.TWITCH_CLIENT_ID!);
  url.searchParams.set('client_secret', process.env.TWITCH_CLIENT_SECRET!);
  url.searchParams.set('code', code);
  url.searchParams.set('grant_type', 'authorization_code');
  url.searchParams.set('redirect_uri', process.env.TWITCH_REDIRECT_URI!);

  const r = await fetch(url, { method: 'POST' });
  if (!r.ok) throw new Error(`twitch token err ${r.status}: ${await r.text()}`);
  return r.json() as Promise<{ access_token: string; refresh_token: string; scope: string[] }>;
}

export async function twitchUser(accessToken: string) {
  const r = await fetch('https://api.twitch.tv/helix/users', {
    headers: {
      'Client-ID': process.env.TWITCH_CLIENT_ID!,
      'Authorization': `Bearer ${accessToken}`,
    },
    cache: 'no-store',
  });
  if (!r.ok) throw new Error(`twitch users err ${r.status}: ${await r.text()}`);
  const data = await r.json();
  return data.data?.[0] as { id: string; login: string; display_name: string } | undefined;
}

export async function twitchLiveStatus(accessToken: string, userId: string) {
  const r = await fetch(`https://api.twitch.tv/helix/streams?user_id=${userId}`, {
    headers: {
      'Client-ID': process.env.TWITCH_CLIENT_ID!,
      'Authorization': `Bearer ${accessToken}`,
    },
    cache: 'no-store',
  });
  if (!r.ok) throw new Error(`twitch streams err ${r.status}: ${await r.text()}`);
  const data = await r.json();
  const live = (data.data && data.data.length > 0) ? data.data[0] : null;
  return live ? { live: true, title: live.title, game: live.game_name } : { live: false };
}
