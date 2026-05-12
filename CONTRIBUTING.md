# Contributing to SLIM

Thank you for your interest in SLIM! We're actively working to improve token savings and expand the format. Contributions are very welcome.

## Ground rules

- All changes to `main` require a **pull request** — direct pushes are blocked.
- Every PR needs **at least one approving review** before it can be merged.
- Keep PRs focused: one feature or fix per PR. Large refactors should start as an issue.

## How to contribute

1. **Open an issue first** for any non-trivial change (new feature, benchmark improvement, spec change) so the direction can be aligned before you write code.
2. Fork the repo and create a branch from `main`:
   ```bash
   git checkout -b feat/my-improvement
   ```
3. Make your changes. For converter changes, edit both `tests/md_to_slm.py` **and** `website/js/slim.js` — they must stay in sync.
4. Run the test suite:
   ```bash
   python tests/md_to_slm.py        # 22 self-tests — must all pass
   python tests/benchmark_runner.py # check your savings impact
   ```
5. Open a pull request against `main`. Fill in the PR template.

## Areas where we'd love help

- **Plain-prose token savings** — finding lossless (or acceptable-lossy) transforms for files without Markdown decoration
- **Corpus expansion** — more real-world CLAUDE.md / AGENT.md / copilot-instructions.md files for the benchmark
- **Editor plugins** — VS Code, IntelliJ, Neovim syntax highlighting and snippets
- **Parser ports** — Go, Rust, TypeScript native implementations
- **Documentation** — examples, tutorials, migration guides

## Code style

- Python: follow existing style (no type annotations beyond the existing ones, no extra dependencies)
- JavaScript: zero-dependency, ES5-compatible, no build step
- Tests: add a `check(...)` case for every new behaviour in `md_to_slm.py`

## Reporting security issues

Please **do not** open a public GitHub issue for security vulnerabilities. Email `hello@slimformat.org` instead.
