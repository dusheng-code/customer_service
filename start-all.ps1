# ============================================================
#  电商客服系统 一键启动脚本
#  （数据库为本地 MySQL，已自行连接，无需本脚本启动）
#  用法：在项目根目录执行  .\start-all.ps1
#  作用：启动 电商后端 + 客服后端 + 前端
# ============================================================

# ---------- 路径配置（$PSScriptRoot = 本脚本所在目录，即项目根）----------
$Root         = $PSScriptRoot
$EcommerceDir = Join-Path $Root "ecommerce-service-backend"
$FrontendDir  = Join-Path $Root "customer-service-frontend"

Write-Host "==== 开始一键启动 ====" -ForegroundColor Cyan
Write-Host "提示：数据库使用本地 MySQL，请确保其已自行运行。" -ForegroundColor DarkGray

# ---------- 1. 启动模拟电商后端（新窗口）----------
Write-Host "[1/3] 启动 电商后端 (18081)..." -ForegroundColor Yellow
$cmdEcom = "Set-Location '$EcommerceDir'; uv sync; uv run python main.py"
Start-Process powershell -ArgumentList '-NoExit', '-Command', $cmdEcom

# 给后端一点启动时间
Start-Sleep -Seconds 3

# ---------- 2. 启动客服后端（新窗口，运行在项目根）----------
Write-Host "[2/3] 启动 客服后端 (18082)..." -ForegroundColor Yellow
$cmdSvc = "Set-Location '$Root'; uv sync; uv run python main.py"
Start-Process powershell -ArgumentList '-NoExit', '-Command', $cmdSvc

# 再给后端一点启动时间，然后拉起前端
Start-Sleep -Seconds 3

# ---------- 3. 启动前端（新窗口）----------
Write-Host "[3/3] 启动 前端 (Vite)..." -ForegroundColor Yellow
$cmdFe = "Set-Location '$FrontendDir'; npm install; npm run dev"
Start-Process powershell -ArgumentList '-NoExit', '-Command', $cmdFe

Write-Host "==== 已全部拉起，各服务在独立窗口中运行，关窗即停,http://127.0.0.1:5173访问即可 ====" -ForegroundColor Green
