# Contributing

1. Install Git LFS, Node.js 24 and Python 3.11 or newer.
2. Clone with `git lfs clone` or run `git lfs pull` after a normal clone.
3. Run `npm ci`.
4. Run `npm run verify:source` and `npm run verify:assets`.
5. Keep generated output out of Git; `dist/` and `release/` are ignored.
6. Never commit user-profile data, account tokens, cookies or Steam tickets.

Changes to recovered binary assets must include regenerated checksum manifests. Run `npm run checksums` and explain why the binary changed in the pull request.
