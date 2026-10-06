[CmdletBinding()]
param(
    [string]$RepoRoot = '',
    [string]$ToolsRoot = 'C:\Nexus-Tools',
    [string]$Query = 'sistemas local-first conhecimento pessoal',
    [string]$AvatarName = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ($env:OS -ne 'Windows_NT') { throw 'NEXUS_WINDOWS_REQUIRED' }
if (-not $RepoRoot) { $RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent }
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$python = Join-Path $RepoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'NEXUS_VENV_REQUIRED: run CONSTRUIR-NEXUS-EXE.bat or prepare-nexus-core.ps1 first.'
}

$null = New-Item -ItemType Directory -Force -Path $ToolsRoot
$reports = Join-Path $ToolsRoot 'reports'
$null = New-Item -ItemType Directory -Force -Path $reports
$stamp = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')
$reportRoot = Join-Path $reports ('real-acceptance-' + $stamp)
$null = New-Item -ItemType Directory -Path $reportRoot

$steps = [ordered]@{}
function Record-Step {
    param([string]$Name, [string]$Status, [string]$Detail, [string]$Log = '')
    $script:steps[$Name] = [ordered]@{
        status = $Status
        detail = $Detail
        log = $Log
    }
    Write-Host (('{0,-24} {1}' -f $Name, $Status))
}

function Invoke-PytestStep {
    param([string]$Name, [string[]]$Targets, [hashtable]$Environment = @{})
    $stdout = Join-Path $reportRoot ($Name + '.stdout.txt')
    $stderr = Join-Path $reportRoot ($Name + '.stderr.txt')
    $old = @{}
    foreach ($key in $Environment.Keys) {
        $old[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
        [Environment]::SetEnvironmentVariable($key, [string]$Environment[$key], 'Process')
    }
    try {
        $args = @('-m','pytest') + $Targets + @('-q','--color=no','-p','no:cacheprovider','-o','pythonpath=.')
        $proc = Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $RepoRoot -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru -Wait -NoNewWindow
        if ($proc.ExitCode -eq 0) {
            Record-Step $Name 'PASS' 'pytest real/contract gate passed' $stdout
            return $true
        }
        Record-Step $Name 'FAIL' ('pytest exit ' + $proc.ExitCode) $stderr
        return $false
    }
    finally {
        foreach ($key in $Environment.Keys) {
            [Environment]::SetEnvironmentVariable($key, $old[$key], 'Process')
        }
    }
}

function Invoke-Probe {
    param([string]$Name, [string]$Command, [string[]]$Arguments = @())
    $stdout = Join-Path $reportRoot ($Name + '.stdout.txt')
    $stderr = Join-Path $reportRoot ($Name + '.stderr.txt')
    $args = @((Join-Path $RepoRoot 'nexus\windows\real_acceptance.py'), $Command, '--output', $reportRoot) + $Arguments
    $proc = Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $RepoRoot -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru -Wait -NoNewWindow
    if ($proc.ExitCode -eq 0) {
        Record-Step $Name 'PASS' 'physical capability completed' $stdout
        return 'PASS'
    }
    if ($proc.ExitCode -eq 2) {
        Record-Step $Name 'NOT_CONFIGURED' 'tool/service/configuration unavailable' $stdout
        return 'NOT_CONFIGURED'
    }
    Record-Step $Name 'FAIL' ('probe exit ' + $proc.ExitCode) $stderr
    return 'FAIL'
}

Write-Host '=== NEXUS REAL WINDOWS ACCEPTANCE ==='
Write-Host ('Repository: ' + $RepoRoot)
Write-Host ('Report:     ' + $reportRoot)
Write-Host ''

Invoke-PytestStep 'host-gate-attacks' @(
    'nexus/tests/test_host.py::test_full_http_flow_and_bypasses',
    'nexus/tests/test_host.py::test_wrong_session_cannot_consume_valid_ticket',
    'nexus/tests/test_host.py::test_ticket_is_bound_to_one_run_and_cannot_approve_another',
    'nexus/tests/test_host.py::test_pending_approval_ticket_does_not_survive_host_restart',
    'nexus/tests/test_host.py::test_invalid_tool_output_never_promotes',
    'nexus/tests/test_reverse_flow.py::test_broken_reverse_chain_never_approves_or_recovers_as_pass',
    'nexus/tests/test_reverse_flow.py::test_valid_json_canonical_provenance_tampering_blocks_restart'
) | Out-Null

$soffice = Get-Command soffice.com -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $soffice) { $soffice = Get-Command soffice.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1 }
if (-not $soffice) {
    $programFilesX86 = [Environment]::GetFolderPath('ProgramFilesX86')
    foreach ($candidate in @(
        (Join-Path $env:ProgramFiles 'LibreOffice\program\soffice.com'),
        (Join-Path $programFilesX86 'LibreOffice\program\soffice.com')
    )) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            $soffice = [pscustomobject]@{ Source = $candidate }
            break
        }
    }
}
if ($soffice) {
    Invoke-PytestStep 'book-writer-real' @('nexus/tests/test_writer_real_libreoffice.py') @{
        NEXUS_REAL_WRITER = '1'
        LIBREOFFICE_EXE = $soffice.Source
    } | Out-Null
} else {
    Record-Step 'book-writer-real' 'NOT_CONFIGURED' 'LibreOffice soffice not found'
}

Invoke-Probe 'zotero-search-real' 'zotero' @('--query', $Query) | Out-Null
Invoke-Probe 'internet-search-real' 'web' @('--query', $Query) | Out-Null
Invoke-Probe 'music-real' 'music' | Out-Null

$podcastState = Invoke-Probe 'podcast-real' 'podcast'
$episodeId = ''
$podcastReport = Join-Path $reportRoot 'open-notebook-podcast.json'
if ($podcastState -eq 'PASS' -and (Test-Path -LiteralPath $podcastReport)) {
    try { $episodeId = (Get-Content -LiteralPath $podcastReport -Raw | ConvertFrom-Json).episode_id } catch {}
}

if ($episodeId) {
    $avatarArgs = @('--episode-id', [string]$episodeId)
    if ($AvatarName) { $avatarArgs += @('--avatar-name', $AvatarName) }
    Invoke-Probe 'visual-podcast-real' 'avatar' $avatarArgs | Out-Null
} else {
    Record-Step 'visual-podcast-real' 'BLOCKED_DEPENDENCY' 'podcast did not produce an episode id'
}

$git = (Get-Command git.exe -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$head = (& $git -C $RepoRoot rev-parse HEAD).Trim()

$integration = [ordered]@{
    verify_and_canonical_gate = 'PROVED_THROUGH_HOST'
    writer_pdf = 'PROVED_THROUGH_HOST_FOR_EXISTING_CONVERSION; BOOK_TEMPLATE_PHYSICAL_GATE_SEPARATE'
    zotero_search = 'PHYSICAL_PROBE_ONLY_NOT_HOST_PROCESS'
    internet_search = 'PHYSICAL_PROBE_ONLY_NOT_HOST_PROCESS'
    ace_step_music = 'PHYSICAL_PROBE_ONLY_NOT_HOST_PROCESS'
    open_notebook_podcast = 'PHYSICAL_PROBE_ONLY_NOT_HOST_PROCESS'
    visual_podcast = 'PHYSICAL_EXTENSION_ONLY_NOT_STORE_PROMOTION'
}

$values = @($steps.Values | ForEach-Object { $_.status })
if ($values -contains 'FAIL') {
    $physicalStatus = 'FAIL'
} elseif (($values -contains 'NOT_CONFIGURED') -or ($values -contains 'BLOCKED_DEPENDENCY')) {
    $physicalStatus = 'INCOMPLETE'
} else {
    $physicalStatus = 'PASS'
}

$summary = [ordered]@{
    schema = 'nexus.real-windows-acceptance.v1'
    status = $physicalStatus
    checked_utc = [DateTime]::UtcNow.ToString('o')
    repository = $RepoRoot
    head = $head
    query = $Query
    report_root = $reportRoot
    steps = $steps
    integration_truth = $integration
    system_e2e = 'INCOMPLETE_UNTIL_EXTERNAL_CAPABILITIES_ENTER_HOST_CREATIVE_HUMAN_GATE'
    note = 'No acceptance probe is allowed to promote an external artefact to Canonical. Canonical bypass/tamper attempts are explicit negative tests.'
}
$summaryPath = Join-Path $reportRoot 'summary.json'
$summary | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Host ''
Write-Host ('NEXUS REAL WINDOWS ACCEPTANCE = ' + $physicalStatus)
Write-Host ('SUMMARY: ' + $summaryPath)
Write-Host 'External media/Zotero/web PASS proves the physical tool only; final Host integration remains a separate gate.'

if ($physicalStatus -eq 'PASS') { exit 0 }
if ($physicalStatus -eq 'INCOMPLETE') { exit 2 }
exit 1
