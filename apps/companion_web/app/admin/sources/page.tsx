import SourcesForm from './SourcesForm';
import { createClient } from '@supabase/supabase-js';

export default async function Page() {
  let docs: any[] = [];
  if (process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY) {
    const supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );
    const { data } = await supabase
      .from('docs')
      .select('id,title,publisher,url,fetched_at')
      .order('fetched_at', { ascending: false })
      .limit(50);
    docs = data ?? [];
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Sources</h1>
      <SourcesForm />
      <table border={1} cellPadding={4} style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>Title</th>
            <th>Publisher</th>
            <th>URL</th>
            <th>Fetched</th>
          </tr>
        </thead>
        <tbody>
          {docs.map((d) => (
            <tr key={d.id}>
              <td>{d.title}</td>
              <td>{d.publisher}</td>
              <td><a href={d.url} target="_blank" rel="noreferrer">{d.url}</a></td>
              <td>{d.fetched_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
