import { NextRequest, NextResponse } from "next/server";
import { supaAdmin } from "../../../lib/supa";
import { discordPost } from "../../../lib/discord";

async function topScores(
  supa: any,
  game = "module-battle",
  days = 1,
  limit = 10,
) {
  const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
  const { data, error } = await supa
    .from("game_scores")
    .select("score, created_at")
    .eq("game", game)
    .gte("created_at", since)
    .order("score", { ascending: false })
    .limit(limit);
  if (error) throw new Error(error.message);
  return data || [];
}
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const supa = supaAdmin();
  const period = req.nextUrl.searchParams.get("period") || "daily";
  const days = period === "weekly" ? 7 : 1;
  const game = req.nextUrl.searchParams.get("game") || "module-battle";
  const list = await topScores(supa, game, days, 10);

  if (!list.length) {
    await discordPost(
      `📊 ${period === "weekly" ? "Weekly" : "Daily"} leaderboard for **${game}**: No scores yet.`,
    );
    return NextResponse.json({ ok: true, posted: 0 });
  }

  const lines = list
    .map(
      (r: any, i: number) =>
        `#${i + 1} — **${r.score}** pts  ·  ${new Date(r.created_at).toLocaleDateString()}`,
    )
    .join("\n");
  await discordPost(
    `📊 ${period === "weekly" ? "Weekly" : "Daily"} leaderboard — **${game}**\n${lines}`,
  );

  return NextResponse.json({ ok: true, posted: list.length });
}
