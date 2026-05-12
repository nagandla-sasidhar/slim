# Cursor Rules — Full-Stack TypeScript Project

[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
[![Prisma](https://img.shields.io/badge/Prisma-5.x-2D3748?logo=prisma)](https://www.prisma.io/docs)

This file configures **Cursor AI** behavior for this repository.

---

## Project Stack

| Layer | Technology | Docs |
|-------|-----------|------|
| Frontend | [Next.js 14](https://nextjs.org/docs) App Router | [App Router Guide](https://nextjs.org/docs/app) |
| Language | [TypeScript 5.4](https://www.typescriptlang.org/docs/) strict mode | [TS Handbook](https://www.typescriptlang.org/docs/handbook/intro.html) |
| Styling | [Tailwind CSS v3](https://tailwindcss.com/docs) | [Tailwind Docs](https://tailwindcss.com/docs/utility-first) |
| ORM | [Prisma 5](https://www.prisma.io/docs) | [Prisma Schema](https://www.prisma.io/docs/concepts/components/prisma-schema) |
| Auth | [NextAuth.js v5](https://authjs.dev/) | [Auth.js Docs](https://authjs.dev/getting-started) |
| Testing | [Vitest](https://vitest.dev/) + [Playwright](https://playwright.dev/) | [Vitest API](https://vitest.dev/api/) |

---

## Coding Conventions

### TypeScript

- Use **`type`** for unions and intersections; **`interface`** for object shapes that may be extended
- All exports are *named exports* — never `export default` except in Next.js page/layout files
- Use `satisfies` operator for config objects: `const config = { ... } satisfies Config`
- Never use `as` type assertions — fix the inference instead

### React / Next.js

- Server Components are the *default* — add `"use client"` only when necessary
- Data fetching goes in **Server Components** or **Route Handlers**, never in client components
- Use **`loading.tsx`** and **`error.tsx`** for route-level loading and error states
- `useEffect` for side effects only — not for derived state (use `useMemo`)

### API Routes

All API routes follow this response shape:

```typescript
// Success
{ data: T; error: null }

// Error
{ data: null; error: { code: string; message: string } }
```

Use `zod` to validate all request bodies:

```typescript
import { z } from "zod"

const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
})
```

---

## File Structure

```
src/
  app/                  # Next.js App Router pages
    (auth)/             # Route group for auth pages
    api/                # API route handlers
  components/           # Shared React components
    ui/                 # Primitive UI components (Button, Input...)
    features/           # Feature-specific components
  lib/                  # Utilities, helpers, service clients
  server/               # Server-only code (db, auth, services)
  types/                # Shared TypeScript types
prisma/
  schema.prisma         # Database schema
  migrations/           # Migration history
```

---

## Do Not

- **`any`** — forbidden everywhere
- **`console.log`** in production code — use the `logger` from `@/lib/logger`
- **`useEffect`** for data fetching — use Server Components or SWR
- Raw SQL strings — use Prisma query API
- Committing `*.env.local` or any file containing credentials
