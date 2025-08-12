import { NextRequest, NextResponse } from 'next/server';
import { supaAdmin } from '@/app/lib/supa';
import { twitchLiveStatus } from '@/app/lib/twitch';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const supa = supaAdmin();
  const { data, error } = await supa
    .from('oauth_tokens')
    .select('*')
    .eq('provider', 'twitch')
    .order('updated_at', { ascending: false })
    .limit(1)
    .maybeSingle();

  if (error || !data) return NextResponse.json({ provider: 'twitch', connected: false });

  const live = await twitchLiveStatus(data.access_token, data.provider_user_id);
  return NextResponse.json({
    provider: 'twitch',
    connected: true,
    login: data.provider_login,
    live: live.live,
    title: (live as any).title ?? null,
    game: (live as any).game ?? null,
  });
}
