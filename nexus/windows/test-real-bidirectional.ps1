# Existing checkout only. Observe physical tools separately from simulated contracts.
# Does not deploy, repair, change user data, or approve Canonical work.
[CmdletBinding()]
param([string]$ReportRoot = '')
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Set-StrictMode -Version Latest

if ($env:OS -cne 'Windows_NT') { throw 'NEXUS_WINDOWS_REQUIRED' }
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
if (-not (Test-Path -LiteralPath (Join-Path $repo '.git'))) { throw 'NEXUS_EXISTING_GIT_CHECKOUT_REQUIRED' }
$git = (Get-Command git.exe -CommandType Application -ErrorAction Stop).Source
$origin = (& $git -C $repo config --get remote.origin.url).Trim()
if ($LASTEXITCODE -ne 0 -or $origin -cne 'https://github.com/PAPACREATOR/cerebro-parvo-.git') { throw 'NEXUS_WRONG_ORIGIN' }
$head = (& $git -C $repo rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -cnotmatch '^[0-9a-f]{40}$') { throw 'NEXUS_HEAD_UNAVAILABLE' }
$dirty = & $git -C $repo status --porcelain --untracked-files=all
if ($LASTEXITCODE -ne 0 -or $dirty) { throw 'NEXUS_DIRTY_TREE' }
if (-not $ReportRoot) {
    if (-not $env:LOCALAPPDATA) { throw 'NEXUS_LOCALAPPDATA_UNAVAILABLE' }
    $ReportRoot = Join-Path $env:LOCALAPPDATA 'Nexus\Relatorios-Testes'
}
if (Test-Path -LiteralPath $ReportRoot) {
    if ((Get-Item -LiteralPath $ReportRoot -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'NEXUS_REPORT_REPARSE_BLOCKED' }
} else {
    $null = New-Item -ItemType Directory -Force -Path $ReportRoot
}
$folder = Join-Path $ReportRoot ('e2e-' + [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $folder
$reportFile = Join-Path $folder 'resultado.json'
$report = [ordered]@{
    schema='nexus.windows.bidirectional-observation.v1'
    status='RUNNING'
    head=$head
    started_utc=[DateTime]::UtcNow.ToString('o')
    finished_utc=$null
    repository=$origin
    report_directory=$folder
    scope='Ephemeral tests; no deployment, human approval, Canonical data or source repair.'
    stages=@()
    not_proven=@('OpenNotebook real model/DB', 'WAV from ACE-Step', 'MP4/Deforum full render', 'Physical PC installation acceptance')
}
function Save-Report {
    $report | ConvertTo-Json -Depth 9 | Set-Content -LiteralPath $reportFile -Encoding UTF8
}
function Record-Stage([string]$Name,[string]$Kind,[string]$Status,[string]$Detail,[string]$Log) {
    $report.stages += [ordered]@{name=$Name;kind=$Kind;status=$Status;detail=$Detail;log=$Log}
    Save-Report
    Write-Host ('NEXUS ' + $Name + ' = ' + $Status + ' ' + $Detail)
}
function Run-Command([string]$Name,[string]$Kind,[string]$Executable,[string[]]$Arguments,[string]$JUnit='', [string]$WorkingDirectory='') {
    $log = Join-Path $folder ($Name + '.log')
    try {
        $cwd = if ($WorkingDirectory) { $WorkingDirectory } else { $repo }
        Push-Location -LiteralPath $cwd
        try {
            & $Executable @Arguments 2>&1 | Out-File -LiteralPath $log -Encoding UTF8
            $code = $LASTEXITCODE
        } finally { Pop-Location }
        if ($null -eq $code -or $code -ne 0) {
            Record-Stage $Name $Kind 'FAIL' ('exit=' + $code) $log
            return $false
        }
        if ($JUnit) {
            if (-not (Test-Path -LiteralPath $JUnit -PathType Leaf)) {
                Record-Stage $Name $Kind 'FAIL' 'JUnit missing' $log
                return $false
            }
            [xml]$xml = Get-Content -LiteralPath $JUnit -Raw
            $skipped = 0; $count = 0
            foreach ($suite in @($xml.SelectNodes('//testsuite'))) {
                $skipped += [int]$suite.skipped
                $count += [int]$suite.tests
            }
            if ($count -eq 0 -or $skipped -gt 0) {
                Record-Stage $Name $Kind 'BLOCKED' ('tests=' + $count + ', skipped=' + $skipped) $log
                return $false
            }
        }
        Record-Stage $Name $Kind 'PASS' 'ver log' $log
        return $true
    } catch {
        Record-Stage $Name $Kind 'FAIL' $_.Exception.Message $log
        return $false
    }
}
function Pytest([string]$Name,[string]$Kind,[string[]]$Targets) {
    $xml = Join-Path $folder ($Name + '.xml')
    $pytestArguments = @('-m','pytest') + $Targets + @('-q','--color=no','-p','no:cacheprovider','-o','pythonpath=.',('--junitxml=' + $xml))
    return Run-Command $Name $Kind $python $pytestArguments $xml
}
function Has-FileEnv([string]$Name) {
    $value = [Environment]::GetEnvironmentVariable($Name,'Process')
    return ($value -and [IO.Path]::IsPathRooted($value) -and (Test-Path -LiteralPath $value -PathType Leaf))
}
$script:python = Join-Path $repo '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    $cmd = Get-Command python.exe -CommandType Application -ErrorAction SilentlyContinue
    $script:python = if ($cmd) { $cmd.Source } else { '' }
}
$oldBytecode = $env:PYTHONDONTWRITEBYTECODE
$oldWriter = $env:NEXUS_REAL_WRITER
$oldLT = $env:NEXUS_REAL_VERIFY_PROOFREAD
$env:PYTHONDONTWRITEBYTECODE = '1'
try {
    Save-Report
    if (-not $python) {
        Record-Stage 'python' 'PREFLIGHT' 'BLOCKED' 'Python 3.12 missing' ''
    } elseif (Run-Command 'python' 'PREFLIGHT' $python @('-c','import sys;assert sys.version_info[:2]==(3,12);print(sys.version)')) {
        if (Run-Command 'integrity' 'PREFLIGHT' $python @('-c',"from nexus.host import verify_integrity;verify_integrity();print('PASS')")) {
            $null = Pytest 'native-folha-shell' 'REAL_WINDOWS_HOST' @('nexus/tests/test_folha_shell_bidirectional_e2e.py','nexus/tests/test_reverse_flow.py','nexus/tests/test_imp001_boundary_additive.py')
            $null = Pytest 'composed-adversarial-learning' 'CONTRACT_AND_NATIVE_LAB' @('nexus/tests/test_folha_tool_composition.py','nexus/tests/test_folha_writer_preexecution.py','nexus/tests/test_procedural_learning_lab.py','nexus/tests/test_frontdoor_adversarial.py')
            # Mock peers bind fixed ports (OpenNotebook 5055, ACE-Step 8001,
            # Forge 7861); never launch them against an owner's live apps.
            # Their adversarial and SSRF regressions stay in the GitHub CI.
            Record-Stage 'notebook-web-boundaries' 'CONTRACT_CI_ONLY' 'NOT_RUN' 'Mock-peer tests reserved for isolated CI' ''
            Record-Stage 'media-security' 'CONTRACT_CI_ONLY' 'NOT_RUN' 'Mock ports reserved for isolated CI' ''
            $null = Run-Command 'ace-forge-local-health' 'REAL_MCP_HEALTH_NOT_RENDER' $python @('nexus/windows/check_media_tools.py','--wait-seconds','0')
            if ((Has-FileEnv 'LIBREOFFICE_EXE') -and (Has-FileEnv 'SANDY_EXE')) {
                $env:NEXUS_REAL_WRITER = '1'
                $null = Pytest 'real-writer-chain' 'REAL_WINDOWS_PDF' @('nexus/tests/test_writer_real_libreoffice.py','nexus/tests/test_native_writer_route_real.py')
                $node = Get-Command node.exe -CommandType Application -ErrorAction SilentlyContinue
                if ($node -and (Test-Path -LiteralPath (Join-Path $repo 'node_modules\playwright'))) {
                    $null = Run-Command 'real-chrome-pdf' 'REAL_CHROME_HOST_PDF' $node.Source @((Join-Path $repo 'nexus/tests/folha_real_writer_browser.cjs')) '' $folder
                } else {
                    Record-Stage 'real-chrome-pdf' 'REAL_CHROME_HOST_PDF' 'BLOCKED' 'Node/Playwright/Chrome not ready' ''
                }
            } else {
                Record-Stage 'real-writer-chain' 'REAL_WINDOWS_PDF' 'BLOCKED' 'LIBREOFFICE_EXE / SANDY_EXE not set' ''
                Record-Stage 'real-chrome-pdf' 'REAL_CHROME_HOST_PDF' 'BLOCKED' 'Writer not configured' ''
            }
            if ((Has-FileEnv 'NEXUS_LANGUAGETOOL_JAVA') -and (Has-FileEnv 'NEXUS_LANGUAGETOOL_JAR')) {
                $env:NEXUS_REAL_VERIFY_PROOFREAD = '1'
                $null = Pytest 'real-languagetool-chain' 'REAL_WINDOWS_TWO_TOOLS' @('nexus/tests/test_native_languagetool_route_real.py')
            } else {
                Record-Stage 'real-languagetool-chain' 'REAL_WINDOWS_TWO_TOOLS' 'BLOCKED' 'LanguageTool Java/JAR not set' ''
            }
        }
    }
} finally {
    $env:PYTHONDONTWRITEBYTECODE = $oldBytecode
    $env:NEXUS_REAL_WRITER = $oldWriter
    $env:NEXUS_REAL_VERIFY_PROOFREAD = $oldLT
    $report.finished_utc = [DateTime]::UtcNow.ToString('o')
    $failed = @($report.stages | Where-Object { $_.status -eq 'FAIL' }).Count -gt 0
    $blocked = @($report.stages | Where-Object { $_.status -eq 'BLOCKED' }).Count -gt 0
    $report.status = if ($failed) {'FAIL'} elseif ($blocked) {'BLOCKED'} else {'PARTIAL_NOT_PROVEN'}
    Save-Report
    Write-Host ('NEXUS ' + $report.status + ' | HEAD: ' + $head)
    Write-Host ('Relatorio: ' + $reportFile)
}
if ($report.status -eq 'FAIL') { exit 1 }
exit 2  # Never claim full product evidence when WAV/MP4/OpenNotebook are not proven.
