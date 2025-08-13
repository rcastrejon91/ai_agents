export async function deploySite(p: { template: string }) {
  // Kick off a Vercel Deploy Hook or create a new project from a template.
  return { status: 'queued', template: p.template, ref: `DEPLOY-${Date.now()}` };
}
