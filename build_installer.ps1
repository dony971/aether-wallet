# AETHER Wallet — Build Installer
#
# Option 1: Inno Setup (recommended)
#   Install Inno Setup 6 from https://jrsoftware.org/isdl.php
#   Then run: ISCC installer.iss
#
# Option 2: Portable ZIP (no dependencies)
#   Run this PowerShell script to create a portable ZIP archive

param(
    [switch]$Portable
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$dist = Join-Path $root "dist\AETHER_Wallet"

if (-not (Test-Path $dist)) {
    Write-Host "Error: dist\AETHER_Wallet not found. Run PyInstaller build first." -ForegroundColor Red
    exit 1
}

if ($Portable) {
    $ver = "1.1.0"
    $zipName = "AETHER_Wallet_v${ver}_Portable.zip"
    $zipPath = Join-Path $root $zipName

    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($dist, $zipPath)

    Write-Host "Portable ZIP created: $zipPath" -ForegroundColor Green
    Write-Host "Size: $([math]::Round((Get-Item $zipPath).Length / 1MB, 1)) MB" -ForegroundColor Green
}
else {
    Write-Host @"
To build the installer:
  1. Install Inno Setup 6 from https://jrsoftware.org/isdl.php
  2. Run: ISCC installer.iss
   3. Output: installer\AETHER_Wallet_v1.0.0_Setup.exe

For a portable ZIP instead, run: .\build_installer.ps1 -Portable
"@
}
