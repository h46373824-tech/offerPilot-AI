# Contributing to OfferPilot AI

Thank you for helping improve OfferPilot AI. Contributions must preserve the project's local-first, source-traceable and privacy-conscious design.

## Before opening a change

1. Create a branch from `dev`.
2. Do not commit `.env`, tokens, resumes, database dumps, logs, scraped page copies, or personal data.
3. Do not add a recruitment source unless its URL, usage basis, verification date, scope and removal path are documented.
4. Do not implement CAPTCHA bypasses, credential reuse, proxy rotation, stealth fingerprints, automatic applications, or access-control circumvention.
5. Keep Demo and verified records distinguishable in the database and interface.

## Local checks

```powershell
cd frontend
npm ci
npm run format:check
npm run lint
npm run typecheck
npm run build

cd ..\backend
python -m pip install -e ".[dev]"
python -m ruff format --check .
python -m ruff check .
python -m mypy app tests
python -m pytest
```

For full-stack changes, run `docker compose up --build -d --wait` and the Playwright suite described in the README.

## Pull requests

Describe the user-visible outcome, data-source impact, migrations, security implications and tests. Keep unrelated changes out of the same pull request. A change is not ready if its documentation or migration is missing.

## License status

No open-source license has been selected yet. Submitting a contribution does not change the repository's current copyright status. Maintainers must select and add a license before presenting the project as open source.
