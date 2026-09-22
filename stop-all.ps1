# ============================================================
#  电商客服系统 一键停止脚本
#  只停止本项目拉起的前后端进程，本地 MySQL 不受影响
#  用法：在项目根目录执行  .\stop-all.ps1
# ============================================================

Write-Host "正在停止后端 uvicorn 进程（数据库为本地 MySQL，不受影响）..." -ForegroundColor Yellow

# 结束用 python 跑的 main.py（按命令行特征过滤，避免误杀其它 python 程序）
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*main.py*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

# 结束前端 vite/node 进程（只匹配本前端目录，避免误杀其它 node 程序）
Get-CimInstance Win32_Process -Filter "Name='node.exe'" |
    Where-Object { $_.CommandLine -like '*customer-service-frontend*' -or $_.CommandLine -like '*vite*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Write-Host "已停止前后端进程。残留窗口可直接手动关闭。" -ForegroundColor Green
