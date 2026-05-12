---
agent: copilot-workspace
project: ecommerce-monorepo
last_updated: 2024-12-01
---

# Copilot Workspace Instructions — E-Commerce Monorepo

[![monorepo](https://img.shields.io/badge/monorepo-turborepo-EF4444)](https://turbo.build/)
[![pnpm](https://img.shields.io/badge/package%20manager-pnpm-F69220)](https://pnpm.io/)

## Workspace Layout

```
apps/
  web/          Next.js 14 storefront
  admin/        React admin dashboard
  api/          Express + tRPC backend
packages/
  ui/           Shared component library
  db/           Prisma schema + client
  auth/         NextAuth shared config
  config/       ESLint, TypeScript configs
```

## Working with This Monorepo

- Always run commands from the **repo root** using `pnpm --filter <package> <command>` or Turborepo tasks
- **Never** `cd` into a package and run `npm install` — it breaks the lockfile
- Add a dependency to a specific package: `pnpm add <dep> --filter @acme/web`
- Run all tests: `pnpm turbo test`
- Build everything: `pnpm turbo build`

## Cross-Package Changes

When changing `packages/db` (Prisma schema):
1. Edit `packages/db/prisma/schema.prisma`
2. Run `pnpm --filter @acme/db prisma migrate dev --name <migration_name>`
3. Run `pnpm --filter @acme/db generate` to regenerate the client
4. **Check** that `apps/api` and `apps/web` compile — they import `@acme/db`

When changing `packages/ui`:
1. Build the package: `pnpm --filter @acme/ui build`
2. Check consuming apps for TypeScript errors: `pnpm turbo typecheck`
3. Update [Storybook](https://storybook.js.org/) stories if you changed a component's API

## Shared Types

All shared types live in `packages/db/src/types.ts` or the individual package's `types.ts`. Do **not** duplicate type definitions across apps. Import from the shared package.

```typescript
// Good
import type { User } from "@acme/db"

// Bad
interface User { id: string; email: string; ... } // local copy
```

## Environment Variables

| Variable | Used in | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `packages/db`, `apps/api` | Postgres connection string |
| `NEXTAUTH_SECRET` | `apps/web`, `apps/admin` | Auth signing secret |
| `STRIPE_SECRET_KEY` | `apps/api` | Stripe API key |
| `NEXT_PUBLIC_API_URL` | `apps/web` | Public API base URL |

Copy `.env.example` to `.env.local` in the repo root. Turborepo passes variables through to each app automatically.

## Troubleshooting

**`Module not found: @acme/ui`** — Run `pnpm install` from root, then `pnpm turbo build --filter=@acme/ui`.

**Type errors after schema change** — Run `pnpm --filter @acme/db generate` then restart TS server in your IDE.

**Turbo cache stale results** — Run `pnpm turbo <task> --force` to bypass cache.

See [internal wiki](https://wiki.internal/monorepo) for more.
