---
skill_set: web-scraping
version: "0.3"
author: dev-team
---

# Skills: **WebScraper Agent**

## Available Tools

| Tool | Description | Returns |
|------|-------------|---------|
| `fetch_page(url)` | GET a URL and return HTML | `string` |
| `parse_links(html)` | Extract all `<a>` tags | `list[str]` |
| `screenshot(url)` | Capture page as PNG | `bytes` |

## Usage Notes

- Always call **`fetch_page`** before **`parse_links`** — they are *not* independent
- `screenshot` is **slow** (~3s) — use sparingly
- All URLs must be *fully qualified*: `https://...` not `/path/to/page`

## Error Handling

If `fetch_page` returns `null`, log `[WARN] fetch failed: {url}` and **skip** that URL. Do **not** retry more than **2 times**.

See also: [Playwright docs](https://playwright.dev/docs/api/class-page) | [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
