import OpenAI from 'openai';
import { createClient } from '@supabase/supabase-js';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export function chunkText(text: string, size = 800, overlap = 100): string[] {
  const chunks: string[] = [];
  let i = 0;
  while (i < text.length) {
    chunks.push(text.slice(i, i + size));
    i += size - overlap;
  }
  return chunks;
}

export async function upsertDocWithChunks(
  doc: { title: string; url: string; publisher: string; license?: string; metadata?: any },
  text: string
): Promise<{ inserted: number; docId: string }> {
  const { data: existing, error: existErr } = await supabase
    .from('docs')
    .select('id')
    .eq('url', doc.url)
    .maybeSingle();
  if (existErr) throw existErr;
  let docId = existing?.id as string | undefined;
  if (!docId) {
    const { data: inserted, error: insErr } = await supabase
      .from('docs')
      .insert({
        title: doc.title,
        url: doc.url,
        publisher: doc.publisher,
        license: doc.license,
        metadata: doc.metadata,
      })
      .select('id')
      .single();
    if (insErr) throw insErr;
    docId = inserted.id;
  }

  const chunks = chunkText(text);
  if (chunks.length === 0) return { inserted: 0, docId: docId! };

  const embeddings = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: chunks,
  });

  const rows = embeddings.data.map((e, i) => ({
    doc_id: docId,
    content: chunks[i],
    embedding: e.embedding,
  }));

  const { error: chunkErr } = await supabase.from('doc_chunks').insert(rows);
  if (chunkErr) throw chunkErr;

  return { inserted: rows.length, docId: docId! };
}

export { openai, supabase };
