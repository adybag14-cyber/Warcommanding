# Contributing

1. Install Node.js 24 and Python 3.11 or newer.
2. Clone the repository normally; Git LFS is not required.
3. Run `npm ci`.
4. Run `npm run verify:source` and `npm run verify:assets`.
5. Use `npm run runtime:restore` to reconstruct the exact recovered Windows runtime locally.
6. Keep generated output out of Git; `runtime/`, `dist/` and `release/` are ignored.
7. Never commit user-profile data, account tokens, cookies or Steam tickets.

Changes to recovered assets or runtime payloads must include regenerated checksum manifests. Run `npm run checksums` and explain every binary change in the pull request.
