import { NextResponse } from 'next/server';

export async function GET() {
  const params = new URLSearchParams({
    client_id: process.env.TWITCH_CLIENT_ID!,
    redirect_uri: process.env.TWITCH_REDIRECT_URI!,
    response_type: 'code',
    scope: ['user:read:email'].join(' '),
  });
  const url = `https://id.twitch.tv/oauth2/authorize?${params.toString()}`;
  return NextResponse.redirect(url);
}
