# Security policy

## Supported branch

Security fixes are accepted against `main`.

## Reporting

Do not open a public issue containing Steam tickets, account identifiers, cookies, access tokens, private CDN URLs, or other credentials. Contact the repository owner privately through GitHub instead.

## Repository hygiene

The committed `seed-assets/asset-cache` contains only static assets and its integrity manifest. Chromium profile data, cookies, local/session storage, account state, Steam session tickets and user settings are intentionally excluded.
