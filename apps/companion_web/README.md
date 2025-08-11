# Companion Web

Next.js frontend for the Companion project.

## Deploy to Vercel

1. Push the repository to GitHub.
2. In Vercel, create a new project and import this repository.
3. When prompted for the root directory, select `apps/companion_web`.
4. Set the following environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - (optional) `STRIPE_SECRET_KEY`
   - (optional) `STRIPE_PRICE_ID`
5. Deploy. Vercel will run `npm run build` using the scripts from `package.json`.

## Local development

```bash
npm install
npm run dev
```
