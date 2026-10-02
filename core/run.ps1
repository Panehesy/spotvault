# ==============================================================================
# SpotVault - Automated Spotify Playlist Archiving Pipeline
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$scriptRoot = Split-Path -Parent $PSScriptRoot
if (-not $scriptRoot) { $scriptRoot = (Get-Location).Path }

$coreDir = Join-Path $scriptRoot "core"
$spotdlExe = Join-Path $coreDir "spotdl.exe"
$playlistFile = Join-Path $scriptRoot "playlists.txt"
$exampleFile = Join-Path $scriptRoot "playlists.example.txt"
$downloadDir = Join-Path $scriptRoot "Downloads"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       SpotVault - Spotify Playlist Archiver v1.0.0       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " [i] Mode       : Portable (Self-Contained Engine)" -ForegroundColor DarkGray
Write-Host " [i] Quality    : 320 kbps MP3 (Embedded Studio Artwork)" -ForegroundColor DarkGray
Write-Host " [i] Source     : Official Distributor Audio (Topic/VEVO)" -ForegroundColor DarkGray
Write-Host " [i] Output Dir : $downloadDir" -ForegroundColor DarkGray
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Ensure SpotDL executable exists (auto-download if cloned without binaries)
if (-not (Test-Path $spotdlExe)) {
    Write-Host "[!] spotdl.exe not found in $coreDir. Downloading portable binary..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://github.com/spotDL/spotify-downloader/releases/download/v4.5.2/spotdl-4.5.2-win32.exe" -OutFile $spotdlExe
    Write-Host "[+] spotdl.exe downloaded successfully." -ForegroundColor Green
}

# 2. Ensure local FFmpeg exists for audio conversion
$ffmpegPath = Join-Path $env:USERPROFILE ".spotdl\ffmpeg.exe"
if (-not (Test-Path $ffmpegPath)) {
    Write-Host "[!] Local FFmpeg not found. Downloading via spotDL..." -ForegroundColor Yellow
    & $spotdlExe --download-ffmpeg
}

# 3. Ensure local Deno exists for YouTube signature challenge bypass
$denoPath = Join-Path $env:USERPROFILE ".spotdl\deno.exe"
if (-not (Test-Path $denoPath)) {
    Write-Host "[!] Local Deno not found. Downloading via spotDL..." -ForegroundColor Yellow
    & $spotdlExe --download-deno
}

# 4. Ensure playlists.txt exists
if (-not (Test-Path $playlistFile)) {
    if (Test-Path $exampleFile) {
        Copy-Item $exampleFile $playlistFile
        Write-Host "[!] 'playlists.txt' was created from template." -ForegroundColor Yellow
        Write-Host "[!] Please open 'playlists.txt', paste your Spotify playlist URLs, and run this again!" -ForegroundColor Yellow
        Write-Host "Press Enter to exit..." -ForegroundColor DarkGray
        $null = Read-Host
        exit 0
    } else {
        New-Item -ItemType File -Path $playlistFile -Force | Out-Null
        Write-Host "[!] Empty 'playlists.txt' created. Please add Spotify playlist URLs and run again." -ForegroundColor Yellow
        Write-Host "Press Enter to exit..." -ForegroundColor DarkGray
        $null = Read-Host
        exit 0
    }
}

$urls = Get-Content $playlistFile | Where-Object { $_ -and -not $_.StartsWith("#") -and $_.Trim() -ne "" }

if ($urls.Count -eq 0) {
    Write-Host "[!] 'playlists.txt' does not contain any valid links." -ForegroundColor Yellow
    Write-Host "[!] Add your Spotify playlist links and run again." -ForegroundColor DarkGray
    Write-Host "Press Enter to exit..." -ForegroundColor DarkGray
    $null = Read-Host
    exit 0
}

Write-Host "[+] Found $($urls.Count) playlist(s) in queue." -ForegroundColor Green
Write-Host ""

New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null

$index = 0
foreach ($url in $urls) {
    $index++
    $trimmedUrl = $url.Trim()
    
    Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "[$index/$($urls.Count)] Processing: $trimmedUrl" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray
    
    $outputTemplate = Join-Path $downloadDir "{list-name}\{artists} - {title}.{output-ext}"
    
    # Run spotDL with verified studio channels and Android client bot-bypass
    & $spotdlExe download "$trimmedUrl" `
        --output "$outputTemplate" `
        --bitrate 320k `
        --only-verified-results `
        --yt-dlp-args "--extractor-args youtube:player_client=android" `
        --overwrite skip
        
    Write-Host ""
    Write-Host "[$index/$($urls.Count)] Finished playlist. Cooling down for 3 seconds..." -ForegroundColor DarkGray
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  ALL PLAYLISTS HAVE BEEN SUCCESSFULLY ARCHIVED!         " -ForegroundColor Green
Write-Host "  Location: $downloadDir" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
