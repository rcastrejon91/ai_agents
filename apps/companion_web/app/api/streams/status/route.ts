import { NextRequest, NextResponse } from "next/server";
import { supaAdmin } from "../../../lib/supa";

async function latestToken(supa: any, provider: "twitch" | "youtube") {
  const { data } = await supa
    .from("oauth_tokens")
    .select("*")
    .eq("provider", provider)
    .order("updated_at", { ascending: false })
    .limit(1)
    .maybeSingle();
  return data;
}

async function twitchLive(
  accessToken: string,
  userId: string,
  clientId: string
) {
  const r = await fetch(
    `https://api.twitch.tv/helix/streams?user_id=${userId}`,
    {
      headers: {
        "Client-ID": clientId,
        Authorization: `Bearer ${accessToken}`,
      },
      cache: "no-store",
    }
  );
  if (!r.ok) throw new Error("twitch streams: " + r.status);
  const d = await r.json();
  const live = !!(d.data && d.data.length);
  const row = live ? d.data[0] : null;
  return { live, title: row?.title, login: undefined };
}

async function youtubeLive(accessToken: string) {
  const r = await fetch(
    "https://www.googleapis.com/youtube/v3/liveBroadcasts?part=snippet,status&broadcastStatus=active&mine=true",
    {
      headers: { Authorization: `Bearer ${accessToken}` },
      cache: "no-store",
    }
  );
  if (!r.ok) throw new Error("yt live: " + r.status);
  const d = await r.json();
  const live = !!(d.items && d.items.length);
  const row = live ? d.items[0] : null;
  return { live, title: row?.snippet?.title };
}

export const dynamic = "force-dynamic";

export async function GET(_req: NextRequest) {
  const supa = supaAdmin();
  const out: any = { twitch: { live: false }, youtube: { live: false } };

  const tw = await latestToken(supa, "twitch");
  if (tw) {
    const now = await twitchLive(
      tw.access_token,
      tw.provider_user_id,
      process.env.TWITCH_CLIENT_ID!
    );
    out.twitch = { live: now.live, title: now.title, login: tw.provider_login };
  }

  const yt = await latestToken(supa, "youtube");
  if (yt) {
    const now = await youtubeLive(yt.access_token);
    out.youtube = {
      live: now.live,
      title: now.title,
      login: yt.provider_login,
    };
  }

  return NextResponse.json(out);
}
