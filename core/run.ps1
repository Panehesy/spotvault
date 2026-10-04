<#
.SYNOPSIS
    SpotVault v1.0.0 PowerShell Automation Script
.DESCRIPTION
    Runs headless download, playlist generation, and ADB sync operations.
#>

param(
    [string]$Url = "",
    [string]$File = "playlists.txt",
    [string]$Format = "mp3",
    [string]$Bitrate = "320k",
    [string]$StorageMode = "standalone",
    [switch]$SyncAdb,
    [switch]$GeneratePlaylists,
    [switch]$Gui
)

$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Set-Location $ProjectRoot

$argsList = @()

if ($Gui) {
    $argsList += "--gui"
} else {
    if ($Url) { $argsList += "--url", $Url }
    if ($File) { $argsList += "--file", $File }
    if ($Format) { $argsList += "--format", $Format }
    if ($Bitrate) { $argsList += "--bitrate", $Bitrate }
    if ($StorageMode) { $argsList += "--storage-mode", $StorageMode }
    if ($SyncAdb) { $argsList += "--sync-adb" }
    if ($GeneratePlaylists) { $argsList += "--generate-playlists" }
}

python spotvault.py @argsList
