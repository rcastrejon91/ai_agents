export type ToolResult = {
  ok: boolean;
  title?: string;
  text?: string;
  data?: any;
  cite?: string;
};
export type Tool = (args: Record<string, string>) => Promise<ToolResult>;

async function j(u: string) {
  const r = await fetch(u);
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
}

export const tools: Record<string, Tool> = {
  async wiki({ q = "" }) {
    if (!q) return { ok: false, text: "Missing q" };
    const d = await j(`/api/free/wiki?q=${encodeURIComponent(q)}`);
    return {
      ok: true,
      title: d.title,
      text: d.summary?.extract || "No summary",
      cite: d.summary?.content_urls?.desktop?.page,
    };
  },
  async dict({ w = "" }) {
    if (!w) return { ok: false, text: "Missing w" };
    const d = await j(`/api/free/dict?w=${encodeURIComponent(w)}`);
    const def =
      d?.[0]?.meanings?.[0]?.definitions?.[0]?.definition || "No definition";
    return {
      ok: true,
      title: w,
      text: def,
      cite: `https://dictionaryapi.dev/`,
    };
  },
  async books({ q = "" }) {
    const d = await j(`/api/free/openlibrary?q=${encodeURIComponent(q)}`);
    const top = d?.docs?.[0];
    return {
      ok: true,
      title: `Book: ${top?.title || "—"}`,
      text: `Author: ${top?.author || "—"} (${top?.year || "—"})`,
      cite: "https://openlibrary.org",
    };
  },
  async geocode({ q = "" }) {
    const d = await j(`/api/free/geocode?q=${encodeURIComponent(q)}`);
    const first = d?.[0];
    return {
      ok: !!first,
      title: first?.display,
      text: first ? `lat ${first.lat}, lon ${first.lon}` : "No result",
      data: first,
      cite: "https://nominatim.openstreetmap.org",
    };
  },
  async reverse({ lat = "", lon = "" }) {
    const d = await j(
      `/api/free/reverse?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`,
    );
    return {
      ok: true,
      title: d?.display,
      text: JSON.stringify(d?.address || {}, null, 2),
      cite: "https://nominatim.openstreetmap.org",
    };
  },
  async weather({ lat = "", lon = "" }) {
    const d = await j(
      `/api/free/weather?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`,
    );
    const t = d?.hourly?.temperature_2m?.[0];
    return {
      ok: true,
      title: "Weather",
      text: t !== undefined ? `Temperature: ${t}°C` : "No data",
      cite: "https://open-meteo.com",
    };
  },
  async hn({ _ = "" }) {
    const d = await j(`/api/free/hn`);
    const top = d?.[0];
    return {
      ok: true,
      title: top?.title || "Hacker News",
      text: top?.url || "",
      cite: top?.url || "https://news.ycombinator.com",
    };
  },
  async rss({ url = "" }) {
    const d = await j(`/api/free/rss?url=${encodeURIComponent(url)}`);
    const i = d?.items?.[0];
    return {
      ok: !!i,
      title: i?.title || "Feed",
      text: i?.link || "No items",
      cite: url,
    };
  },
};
