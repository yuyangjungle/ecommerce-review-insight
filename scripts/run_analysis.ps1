param(
  [ValidateSet("v1", "v2")]
  [string]$PromptVersion = "v2"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$datasetPath = Join-Path $projectRoot "data\sample\wireless-earbuds-demo.json"
$outputPath = Join-Path $projectRoot "data\sample\wireless-earbuds-analysis.json"
$scriptPath = Join-Path $projectRoot "apps\api\mock_pipeline.py"

python $scriptPath --dataset $datasetPath --output $outputPath --prompt-version $PromptVersion

Write-Host ""
Write-Host "分析结果已生成：" -ForegroundColor Green
Write-Host $outputPath
