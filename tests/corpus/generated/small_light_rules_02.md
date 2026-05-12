# Rules for Code Review Agent

These rules govern how the agent behaves during code review tasks.

## General Rules

- Review only the files listed in the pull request diff
- Do not suggest rewrites unless the code has bugs or serious quality issues
- Keep comments short and actionable
- Assign severity: info, warning, or error

## What to Check

- Logic errors and off-by-one mistakes
- Missing null checks or error handling
- Unused imports and dead code
- Inconsistent naming conventions

## What to Skip

- Style preferences that aren't enforced by a linter
- Framework-specific patterns the author chose deliberately
- Comments about what code "should" do if it does what the PR says

## Tone

Be direct. Avoid phrases like "you might want to consider". Say what the problem is and what to do about it.
