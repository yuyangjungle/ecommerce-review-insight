param(
  [string]$BaseUrl = "http://127.0.0.1:8766",
  [string]$OutputDir = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

function Get-BrowserPath {
  $candidates = @(
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
  )

  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
      return $candidate
    }
  }

  throw "No Edge or Chrome executable was found."
}

function Join-QueryUrl {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Url,
    [string]$Query = ""
  )

  if ([string]::IsNullOrWhiteSpace($Query)) {
    return $Url
  }

  if ($Url.Contains("?")) {
    return "${Url}&${Query}"
  }

  return "${Url}?${Query}"
}

function New-ScreenshotSvg {
  param(
    [Parameter(Mandatory = $true)]
    [string]$BrowserPath,
    [Parameter(Mandatory = $true)]
    [string]$Url,
    [Parameter(Mandatory = $true)]
    [string]$BaseName,
    [Parameter(Mandatory = $true)]
    [int]$Width,
    [Parameter(Mandatory = $true)]
    [int]$Height,
    [Parameter(Mandatory = $true)]
    [string]$TempDir,
    [Parameter(Mandatory = $true)]
    [string]$OutputDir
  )

  $pngPath = Join-Path $TempDir "${BaseName}.png"
  $svgPath = Join-Path $OutputDir "${BaseName}.svg"
  $profileDir = Join-Path $TempDir ("profile-" + $BaseName)
  New-Item -ItemType Directory -Force -Path $profileDir | Out-Null

  $arguments = @(
    "--headless"
    "--disable-gpu"
    "--hide-scrollbars"
    "--window-size=${Width},${Height}"
    "--virtual-time-budget=7000"
    "--run-all-compositor-stages-before-draw"
    "--user-data-dir=$profileDir"
    "--screenshot=$pngPath"
    $Url
  )

  & $BrowserPath @arguments | Out-Null
  Start-Sleep -Milliseconds 250

  if (Test-Path -LiteralPath $pngPath) {
    $image = [System.Drawing.Image]::FromFile($pngPath)
    $jpegCodec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" } | Select-Object -First 1
    $encoder = [System.Drawing.Imaging.Encoder]::Quality
    $encoderParams = [System.Drawing.Imaging.EncoderParameters]::new(1)
    $encoderParams.Param[0] = [System.Drawing.Imaging.EncoderParameter]::new($encoder, [long]78)
    $memory = [System.IO.MemoryStream]::new()

    try {
      $image.Save($memory, $jpegCodec, $encoderParams)
      $base64 = [Convert]::ToBase64String($memory.ToArray())
    } finally {
      $memory.Dispose()
      $encoderParams.Dispose()
      $image.Dispose()
    }

    $svg = @"
<svg xmlns="http://www.w3.org/2000/svg" width="$Width" height="$Height" viewBox="0 0 $Width $Height" role="img" aria-label="$BaseName">
  <image width="$Width" height="$Height" href="data:image/jpeg;base64,$base64" />
</svg>
"@
    [System.IO.File]::WriteAllText($svgPath, $svg, [System.Text.UTF8Encoding]::new($false))
    Remove-Item -LiteralPath $pngPath -Force
    Remove-Item -LiteralPath $profileDir -Recurse -Force -ErrorAction SilentlyContinue
    return $svgPath
  }

  throw "Screenshot was not created for $Url."
}

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
  $OutputDir = Join-Path (Split-Path -Parent $PSScriptRoot) "docs\assets"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$browserPath = Get-BrowserPath
$tempDir = Join-Path $env:TEMP ("codex-shot-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

try {
  $shots = @(
    @{ name = "hero-overview"; query = ""; width = 1440; height = 1400 }
    @{ name = "insight-panels"; query = "section=insights"; width = 1440; height = 1500 }
    @{ name = "prompt-compare"; query = "autoCompare=1&section=compare"; width = 1440; height = 720 }
  )

  $created = foreach ($shot in $shots) {
    $url = Join-QueryUrl -Url $BaseUrl -Query $shot.query
    New-ScreenshotSvg -BrowserPath $browserPath -Url $url -BaseName $shot.name -Width $shot.width -Height $shot.height -TempDir $tempDir -OutputDir $OutputDir
  }

  Write-Output "Screenshots generated:"
  $created | ForEach-Object { Write-Output $_ }
} finally {
  if (Test-Path -LiteralPath $tempDir) {
    Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
  }
}
