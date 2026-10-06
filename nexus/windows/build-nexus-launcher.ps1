[CmdletBinding()]
param(
    [string]$RepoRoot = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ($env:OS -ne 'Windows_NT') {
    throw 'NEXUS_WINDOWS_REQUIRED'
}

if (-not $RepoRoot) {
    $RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

$source = Join-Path $PSScriptRoot 'NexusLauncher.cs'
$python = Join-Path $RepoRoot '.venv\Scripts\python.exe'
$app = Join-Path $RepoRoot 'nexus\app.py'
$out = Join-Path $RepoRoot 'Nexus.exe'

foreach ($required in @($source, $python, $app)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw ('NEXUS_LAUNCHER_REQUIREMENT_MISSING: ' + $required)
    }
}

$candidates = @(
    (Get-Command csc.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source),
    (Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'),
    (Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe')
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

$csc = $candidates | Select-Object -First 1
if (-not $csc) {
    throw 'NEXUS_CSC_NOT_FOUND: .NET Framework C# compiler unavailable.'
}

if (Test-Path -LiteralPath $out) {
    Remove-Item -LiteralPath $out -Force
}

& $csc /nologo /target:exe /optimize+ ('/out:' + $out) $source
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $out)) {
    throw 'NEXUS_LAUNCHER_BUILD_FAILED'
}

# Smoke tests exercise the compiled launcher, the real venv and Windows quoting.
& $out --help | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'NEXUS_LAUNCHER_SMOKE_FAILED' }
$spacePath = Join-Path $env:TEMP 'Nexus Launcher Smoke Data'
& $out --data $spacePath --help | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'NEXUS_LAUNCHER_SMOKE_FAILED'
}

$hash = (Get-FileHash -LiteralPath $out -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host 'NEXUS EXE = PASS'
Write-Host ('FILE: ' + $out)
Write-Host ('SHA256: ' + $hash)
