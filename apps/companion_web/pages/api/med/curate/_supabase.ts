import { createClient } from "@supabase/supabase-js";

export const sb = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE!
);

export const guard = (req: any, res: any) => {
  if (req.headers.authorization !== `Bearer ${process.env.ADMIN_TOKEN}`) {
    res.status(401).json({ error: "Unauthorized" });
    return false;
  }
  return true;
};
