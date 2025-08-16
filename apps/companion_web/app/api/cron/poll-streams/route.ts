import { NextRequest, NextResponse } from "next/server";
import { supaAdmin } from "../../../lib/supa";
import { discordPost } from "../../../lib/discord";

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
  clientId: string,
) {
  const r = await fetch(
    `https://api.twitch.tv/helix/streams?user_id=${userId}`,
    {
      headers: {
        "Client-ID": clientId,
        Authorization: `Bearer ${accessToken}`,
      },
      cache: "no-store",
    },
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
    },
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
  const out: any = { ok: true, events: [] };

  // Twitch
  const tw = await latestToken(supa, "twitch");
  if (tw) {
    const now = await twitchLive(
      tw.access_token,
      tw.provider_user_id,
      process.env.TWITCH_CLIENT_ID!,
    );
    const { data: st } = await supa
      .from("stream_status")
      .select("*")
      .eq("provider", "twitch")
      .eq("provider_user_id", tw.provider_user_id)
      .maybeSingle();

    const wasLive = st?.live ?? false;
    if (now.live !== wasLive) {
      await supa.from("stream_status").upsert(
        {
          provider: "twitch",
          provider_user_id: tw.provider_user_id,
          login: tw.provider_login,
          live: now.live,
          last_change: new Date().toISOString(),
        },
        { onConflict: "provider,provider_user_id" },
      );

      if (now.live) {
        await discordPost(
          `🔴 **Twitch LIVE** — ${tw.provider_login} just went live: ${now.title ?? ""}\nhttps://twitch.tv/${tw.provider_login}`,
        );
        out.events.push("twitch_live_started");
      } else {
        await discordPost(`⚫ Twitch stream ended — ${tw.provider_login}`);
        out.events.push("twitch_live_ended");
      }
    }
  }

  // YouTube
  const yt = await latestToken(supa, "youtube");
  if (yt) {
    const now = await youtubeLive(yt.access_token);
    const { data: st } = await supa
      .from("stream_status")
      .select("*")
      .eq("provider", "youtube")
      .eq("provider_user_id", yt.provider_user_id)
      .maybeSingle();

    const wasLive = st?.live ?? false;
    if (now.live !== wasLive) {
      await supa.from("stream_status").upsert(
        {
          provider: "youtube",
          provider_user_id: yt.provider_user_id,
          login: yt.provider_login,
          live: now.live,
          last_change: new Date().toISOString(),
        },
        { onConflict: "provider,provider_user_id" },
      );

      if (now.live) {
        await discordPost(
          `🔴 **YouTube LIVE** — ${yt.provider_login} just went live: ${now.title ?? ""}\nhttps://youtube.com/channel/${yt.provider_user_id}/live`,
        );
        out.events.push("youtube_live_started");
      } else {
        await discordPost(`⚫ YouTube stream ended — ${yt.provider_login}`);
        out.events.push("youtube_live_ended");
      }
    }
  }

  return NextResponse.json(out);
}
