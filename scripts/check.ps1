$ErrorActionPreference = "Stop"
Push-Location frontend
npm run lint
npm run typecheck
npm run build
Pop-Location
Push-Location backend
ruff check .
ruff format --check .
mypy app tests
pytest
Pop-Location
