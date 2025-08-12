import { NextRequest, NextResponse } from 'next/server';
import { supaAdmin } from '@/app/lib/supa';
import { twitchTokenFromCode, twitchUser } from '@/app/lib/twitch';

export async function GET(req: NextRequest) {
  const code = req.nextUrl.searchParams.get('code');
  if (!code) return NextResponse.redirect('/games?error=missing_code');

  try {
    const token = await twitchTokenFromCode(code);
    const user = await twitchUser(token.access_token);
    if (!user) return NextResponse.redirect('/games?error=no_user');

    const supa = supaAdmin();
    await supa.from('oauth_tokens').upsert({
      provider: 'twitch',
      provider_user_id: user.id,
      provider_login: user.login,
      access_token: token.access_token,
      refresh_token: token.refresh_token,
      scope: (token.scope || []).join(' ')
    }, { onConflict: 'provider,provider_user_id' });

    return NextResponse.redirect('/games?connected=twitch');
  } catch (e: any) {
    return NextResponse.redirect('/games?error=' + encodeURIComponent(e.message || 'twitch_fail'));
  }
}
