# MLB Fantasy Web

Next.js frontend for the MLB Fantasy Baseball application.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy environment variables:
   ```bash
   cp .env.local.example .env.local
   ```

3. Edit `.env.local` with your Supabase credentials:
   - `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase project URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Your Supabase anon/public key

## Development

Start the development server:
```bash
npm run dev
```

Or use the root Makefile:
```bash
make web-dev
```

The app will be available at http://localhost:3000

## Architecture

- **Framework:** Next.js 14+ with App Router
- **Styling:** Tailwind CSS + shadcn/ui
- **Auth:** Supabase client SDK
- **API:** Calls to FastAPI backend at http://localhost:8000

## Project Structure

```
app/
├── (auth)/           # Public auth pages
│   ├── login/
│   ├── signup/
│   └── forgot-password/
├── (protected)/      # Auth-required pages
│   ├── dashboard/
│   └── profile/
├── layout.tsx
└── page.tsx          # Landing page

components/
├── ui/               # shadcn/ui components
├── auth/             # Auth form components
├── profile/          # Profile components
└── layout/           # Header, navigation

lib/
├── supabase/         # Supabase client setup
└── api/              # FastAPI client
```
