import dynamic from "next/dynamic";
const AdminHealthPanel = dynamic(
  () => import("../../components/AdminHealthPanel"),
  { ssr: false }
);

export default function AdminPage() {
  return (
    <main className="mx-auto max-w-4xl p-4">
      <h1 className="text-2xl font-serif mb-4">Admin</h1>
      <AdminHealthPanel />
      <p className="mt-6 text-xs text-zinc-500">
        Demo-only. No clinical use. All data is synthetic. For emergencies, call
        your local emergency number.
      </p>
    </main>
  );
}
