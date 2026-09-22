# Terminal welcome and local Homebrew release

Status: complete

## Scope

- Provide a real terminal logo and the approved English tagline.
- Show welcome after checkout installation, on an empty default launch, and via `welcome`.
- Keep explicit daily commands concise; preserve offline SQLite behavior.
- Package a standalone Homebrew installation and verify it locally.
- Commit the current UI, assets, packaging, documentation and tests.
- Public GitHub/Tap publishing remains a separate step; no remote is configured.

## Verification

- 12 CLI tests passed, including welcome without database creation and normal command behavior.
- Python compilation and Git whitespace checks passed.
- Welcome inspected at 44 and 24 columns; installer welcome checked in a temporary directory.
- `brew install` and `brew reinstall local/oned1t/one-day-one-thing` succeeded.
- `brew test local/oned1t/one-day-one-thing` passed all seven command checks.
- Cellar entry exercised from `/` with isolated data: add/done/month/history/calendar/undo.
- User command resolves to `/opt/homebrew/bin/1d1t`, version 0.1.0.
- Old checkout symlink retained as `~/.local/bin/1d1t-checkout-backup`.
- Tests used temporary data; user records were not modified.

Homebrew upgraded python@3.13, ca-certificates, openssl@3, sqlite and xz during installation.
