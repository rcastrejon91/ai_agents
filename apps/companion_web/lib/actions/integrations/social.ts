export async function postSocial(p: Record<string, any>) {
  // Start by drafting content for review; later post via Graph/TikTok APIs.
  return {
    status: "drafted",
    platforms: p.platforms ?? ["facebook", "instagram", "tiktok"],
  };
}
