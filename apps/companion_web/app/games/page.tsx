"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const GAMES = [
  {
    id: "module-battle",
    title: "Module Battle",
    blurb:
      "Use AI “skills” (fire/ice/mind) to beat glitches. Short runs, high scores.",
  },
  {
    id: "dream-arena",
    title: "Dream Arena",
    blurb: "Surreal prompts from the Imagination Core. Story-driven bouts.",
  },
  {
    id: "guardian-defense",
    title: "Guardian Defense",
    blurb: "Scan threats, counter with safety moves. Beat the risk score.",
  },
];

export default function GamesPage() {
  const [active, setActive] = useState<string>("module-battle");
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    async function poll() {
      try {
        const res = await fetch("/api/streams/status", { cache: "no-store" });
        const data = await res.json();
        setIsLive(!!(data.twitch?.live || data.youtube?.live));
      } catch (err) {
        console.error("poll status failed", err);
      } finally {
        timer = setTimeout(poll, 15000);
      }
    }
    poll();
    return () => clearTimeout(timer);
  }, []);

  return (
    <main className="min-h-screen px-6 py-10 bg-black text-white">
      <header className="mb-8">
        <h1 className="text-3xl font-semibold flex items-center gap-2">
          Games{" "}
          {isLive && (
            <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-red-600 text-white">
              LIVE
            </span>
          )}
        </h1>
        <p className="text-sm text-zinc-400">
          Just for fun. Your core app stays separate.
        </p>
      </header>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {GAMES.map((g) => (
          <button
            key={g.id}
            onClick={() => setActive(g.id)}
            className={`relative px-4 py-2 rounded-md border border-zinc-800 transition
              ${active === g.id ? "bg-zinc-900" : "bg-zinc-950 hover:bg-zinc-900"}`}
          >
            <span className="text-sm">{g.title}</span>
            {active === g.id && (
              <motion.div
                layoutId="pill"
                className="absolute inset-0 rounded-md ring-1 ring-cyan-400/30"
                transition={{ type: "spring", stiffness: 400, damping: 30 }}
              />
            )}
          </button>
        ))}
      </div>

      {/* Animated panel switch */}
      <div className="relative">
        <AnimatePresence mode="wait">
          <motion.section
            key={active}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.18 }}
            className="rounded-xl border border-zinc-800 bg-zinc-950 p-5"
          >
            <GamePanel id={active} />
          </motion.section>
        </AnimatePresence>
      </div>
    </main>
  );
}

function GamePanel({ id }: { id: string }) {
  const game = GAMES.find((g) => g.id === id)!;
  return (
    <div className="grid gap-4 md:grid-cols-[1fr,320px]">
      <div>
        <h2 className="text-xl font-medium">{game.title}</h2>
        <p className="text-zinc-400 text-sm mb-4">{game.blurb}</p>
        <IframePreview id={id} />
      </div>
      <Sidebar id={id} />
    </div>
  );
}

function IframePreview({ id }: { id: string }) {
  // Later: replace with your actual web UIs for each game. For now, placeholder.
  return (
    <div
      className="aspect-video rounded-lg border border-zinc-800 bg-gradient-to-br from-zinc-900 to-black
                    flex items-center justify-center text-zinc-400"
    >
      <span>
        Game canvas for <b>{id}</b> goes here
      </span>
    </div>
  );
}

function Sidebar({ id }: { id: string }) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-black/40 p-4">
      <h3 className="font-medium mb-2">Actions</h3>
      <div className="flex flex-col gap-2">
        <button className="px-3 py-2 rounded-md bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-700/40">
          Start
        </button>
        <button className="px-3 py-2 rounded-md bg-zinc-800 hover:bg-zinc-700 border border-zinc-700">
          How to Play
        </button>
        <button className="px-3 py-2 rounded-md bg-zinc-900 hover:bg-zinc-800 border border-zinc-800">
          Leaderboard
        </button>
      </div>
      <div className="mt-4 text-xs text-zinc-500">
        Switching tabs uses animated transitions (Framer Motion). Core app
        unaffected.
      </div>
    </div>
  );
}
