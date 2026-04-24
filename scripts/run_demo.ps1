$ErrorActionPreference = "Stop"

param(
  [int]$Port = 8765
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$scriptPath = Join-Path $projectRoot "apps\api\server.py"

Write-Host "正在启动本地演示服务：http://127.0.0.1:$Port" -ForegroundColor Green
python $scriptPath --host 127.0.0.1 --port $Port
