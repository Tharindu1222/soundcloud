# Build SCDownloader.exe (PyInstaller) and optional Setup.exe (Inno Setup).
# Run from project root in PowerShell:  .\build.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if (-not (Test-Path 'vendor\ffmpeg.exe')) {
    Write-Warning 'vendor\ffmpeg.exe not found. Read vendor\README.txt - then bundle ffmpeg before release (see vendor\README.txt).'
}

Write-Host "Running PyInstaller..." -ForegroundColor Cyan
python -m PyInstaller --clean --noconfirm SCDownloader.spec

$iscc = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($iscc) {
    Write-Host "Compiling installer with Inno Setup..." -ForegroundColor Cyan
    & $iscc 'installer\SCDownloader.iss'
    Write-Host 'Done. Output: dist_installer\SCDownloader_Setup.exe' -ForegroundColor Green
} else {
    Write-Warning 'Inno Setup 6 not found. Install from https://jrsoftware.org/isinfo.php then re-run this script, or zip dist\SCDownloader yourself.'
    Write-Host 'Portable app folder: dist\SCDownloader' -ForegroundColor Green
}
