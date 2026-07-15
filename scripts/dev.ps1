$ErrorActionPreference = "Stop"
Write-Host "基础设施: docker compose up -d postgres redis"
Write-Host "后端: cd backend; uvicorn app.main:app --reload"
Write-Host "前端: cd frontend; npm run dev"
