[CmdletBinding()]
param(
    [string]$RepoRoot = '',
    [string]$ToolsRoot = 'C:\Nexus-Tools'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ($env:OS -ne 'Windows_NT' -or -not [Environment]::Is64BitOperatingSystem) {
    throw 'NEXUS_WINDOWS_X64_REQUIRED'
}
if (-not $RepoRoot) {
    $RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$ToolsRoot = (Resolve-Path -LiteralPath $ToolsRoot).Path
$installReportPath = Join-Path $ToolsRoot 'complete-install-report.json'
$reportPath = Join-Path $ToolsRoot 'post-install-acceptance-report.json'

$report = [ordered]@{
    schema = 'nexus.post-install-acceptance.v1'
    status = 'RUNNING'
    started_utc = [DateTime]::UtcNow.ToString('o')
    finished_utc = $null
    repo_root = $RepoRoot
    tools_root = $ToolsRoot
    nexus_head = $null
    install_head = $null
    stages = [ordered]@{}
    legacy_accounts_present = @()
    physical_limits = @(
        'This acceptance verifies installed runtimes, CUDA visibility, deterministic/security flows and real MCP calls.',
        'It does not claim a documentary/music/podcast render is artistically correct.',
        'Public Host routes that are intentionally not integrated remain BLOCKED by contract.'
    )
    error = $null
}

function Save-Report {
    $report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $reportPath -Encoding UTF8
}

function Stage-Pass([string]$Name, [object]$Value) {
    $report.stages[$Name] = [ordered]@{ status='PASS'; evidence=$Value }
    Save-Report
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [string[]]$Arguments = @(),
        [string]$WorkingDirectory = $RepoRoot
    )
    Push-Location -LiteralPath $WorkingDirectory
    try {
        $output = & $FilePath @Arguments 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) {
            throw ('NEXUS_COMMAND_FAILED: ' + $FilePath + ' ' + ($Arguments -join ' ') + [Environment]::NewLine + $output)
        }
        return $output.Trim()
    }
    finally {
        Pop-Location
    }
}

function Run-Pytest {
    param([string]$Name, [string[]]$Targets, [hashtable]$Environment = @{})
    $python = Join-Path $RepoRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python)) { throw 'NEXUS_VENV_MISSING' }
    $saved = @{}
    foreach ($key in $Environment.Keys) {
        $saved[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
        [Environment]::SetEnvironmentVariable($key, [string]$Environment[$key], 'Process')
    }
    try {
        $args = @('-m','pytest') + $Targets + @('-q','-p','no:cacheprovider','-o','pythonpath=.')
        $out = Invoke-Checked $python $args $RepoRoot
        Stage-Pass $Name $out
    }
    finally {
        foreach ($key in $Environment.Keys) {
            [Environment]::SetEnvironmentVariable($key, $saved[$key], 'Process')
        }
    }
}

try {
    Save-Report
    if (-not (Test-Path -LiteralPath $installReportPath)) { throw 'NEXUS_INSTALL_REPORT_MISSING' }
    $install = Get-Content -LiteralPath $installReportPath -Raw | ConvertFrom-Json
    if ($install.status -ne 'PASS') { throw ('NEXUS_INSTALL_NOT_PASS: ' + $install.status) }
    $report.install_head = $install.nexus_head

    $git = $install.tools.git.path
    if (-not (Test-Path -LiteralPath $git)) { throw 'NEXUS_GIT_MISSING_AFTER_INSTALL' }
    $head = (Invoke-Checked $git @('rev-parse','HEAD') $RepoRoot).Trim()
    $report.nexus_head = $head
    if ($head -ne $install.nexus_head) { throw 'NEXUS_INSTALL_HEAD_MISMATCH: install and test must use the same exact revision.' }
    $dirty = (Invoke-Checked $git @('status','--porcelain=v1','--untracked-files=all') $RepoRoot).Trim()
    if ($dirty) { throw 'NEXUS_DIRTY_TREE: acceptance requires the exact installed source tree.' }
    Stage-Pass 'install-report' ([ordered]@{status=$install.status; head=$head})

    # Current isolation model: no reusable Nexus/NexusTool credentials.
    foreach ($name in @('Nexus','NexusTool')) {
        $account = Get-LocalUser -Name $name -ErrorAction SilentlyContinue
        if ($account) { $report.legacy_accounts_present += $name }
    }
    $sandbox = Get-Content -LiteralPath (Join-Path $RepoRoot 'nexus\windows_sandbox.py') -Raw
    foreach ($required in @('CreateAppContainerProfile','CreateJobObjectW','AssignProcessToJobObject','DeleteAppContainerProfile')) {
        if ($sandbox -notmatch [regex]::Escape($required)) { throw ('NEXUS_APPCONTAINER_CONTRACT_MISSING: ' + $required) }
    }
    foreach ($forbidden in @('LogonUser','CreateProcessAsUser','NexusTool')) {
        if ($sandbox -match [regex]::Escape($forbidden)) { throw ('NEXUS_REUSABLE_TOOL_IDENTITY_FOUND: ' + $forbidden) }
    }
    Stage-Pass 'windows-task-identity' ([ordered]@{mode='per-task AppContainer'; legacy_accounts=$report.legacy_accounts_present})

    $launcher = $install.launcher.path
    if (-not (Test-Path -LiteralPath $launcher)) { throw 'NEXUS_LAUNCHER_MISSING' }
    foreach ($name in @('languagetool.json','libreoffice.json','open-notebook.json','open-notebook-documentary.json','open-notebook-product.json','moneyprinterturbo.json')) {
        if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot ('nexus\runtime\' + $name)))) {
            throw ('NEXUS_RUNTIME_CONFIG_MISSING: ' + $name)
        }
    }
    Stage-Pass 'launcher-and-runtime' ([ordered]@{launcher=$launcher})

    # Installed executable/runtime smoke checks use exact installer paths.
    $versions = [ordered]@{}
    $versions.git = Invoke-Checked $install.tools.git.path @('--version')
    $versions.python = Invoke-Checked $install.tools.python312.path @('--version')
    $versions.node = Invoke-Checked $install.tools.node.path @('--version')
    $versions.java = Invoke-Checked $install.tools.java.path @('-version')
    $versions.libreoffice = Invoke-Checked $install.tools.libreoffice.path @('--version')
    $versions.ffmpeg = (Invoke-Checked $install.tools.ffmpeg.path @('-version')).Split([Environment]::NewLine)[0]
    if (-not (Test-Path -LiteralPath $install.tools.zotero.path)) { throw 'NEXUS_ZOTERO_MISSING' }
    $versions.zotero = (Get-Item -LiteralPath $install.tools.zotero.path).VersionInfo.FileVersion
    $ollamaList = Invoke-Checked $install.tools.ollama.path @('list')
    if ($ollamaList -notmatch 'qwen3:4b' -or $ollamaList -notmatch 'nomic-embed-text') { throw 'NEXUS_OLLAMA_MODELS_MISSING' }
    $versions.ollama = 'qwen3:4b + nomic-embed-text'
    Stage-Pass 'installed-runtimes' $versions

    # GPU/runtime proof without claiming a real render.
    $forgePython = Join-Path $install.tools.forge.path 'venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $forgePython)) { throw 'NEXUS_FORGE_PYTHON_MISSING' }
    $forgeCuda = Invoke-Checked $forgePython @('-c','import torch; assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0))') $install.tools.forge.path
    Stage-Pass 'forge-cuda' $forgeCuda

    $mediaReport = Get-Content -LiteralPath (Join-Path $ToolsRoot 'nexus-media-tools.json') -Raw | ConvertFrom-Json
    $uv = $install.tools.uv.path
    $aceImport = Invoke-Checked $uv @('run','--no-sync','python','-c','import acestep; import acestep.api_server; print("ACE_STEP_IMPORT=PASS")') $mediaReport.ace_step.path
    Stage-Pass 'ace-step-runtime' $aceImport

    $mptRoot = $install.tools.moneyprinterturbo.path
    $mptHelp = Invoke-Checked $uv @('run','--frozen','python','cli.py','--help') $mptRoot
    Stage-Pass 'moneyprinterturbo-cli' (($mptHelp -split [Environment]::NewLine | Select-Object -First 5) -join [Environment]::NewLine)

    # Standard Nexus blocks first.
    foreach ($suite in @('core','blocks','practical')) {
        $dir = Join-Path $ToolsRoot ('post-install-' + $suite)
        if (Test-Path -LiteralPath $dir) { Remove-Item -LiteralPath $dir -Recurse -Force }
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot 'nexus\windows\check-nexus.ps1') -PythonPath (Join-Path $RepoRoot '.venv\Scripts\python.exe') -Suite $suite -ReportDirectory $dir
        if ($LASTEXITCODE -ne 0) { throw ('NEXUS_POST_INSTALL_SUITE_FAILED: ' + $suite) }
        $state = Get-Content -LiteralPath (Join-Path $dir 'state.json') -Raw | ConvertFrom-Json
        if ($state.status -ne 'PASS') { throw ('NEXUS_POST_INSTALL_SUITE_NOT_PASS: ' + $suite) }
        Stage-Pass ('suite-' + $suite) $state
    }

    # Product/system stress. These use temp data only and cannot promote Canonical.
    Run-Pytest 'product-flows-30000' @('nexus/tests/test_product_flows_5000.py')
    Run-Pytest 'public-routes-6x10000' @('nexus/tests/test_public_product_routes_10000.py')
    Run-Pytest 'public-routes-all-50000' @('nexus/tests/test_public_product_routes_all_50000.py')
    Run-Pytest 'product-system-50000' @('nexus/tests/test_product_system_50000.py')
    Run-Pytest 'product-themes-canonical-200000' @('nexus/tests/test_product_themes_canonical_200k.py')
    Run-Pytest 'varied-200000' @('nexus/tests/test_system_varied_200k.py')
    Run-Pytest 'authority-and-native-boundary' @(
        'nexus/security_tests/test_authority_10000.py',
        'nexus/security_tests/test_native_boundary.py',
        'nexus/security_tests/test_confinement_gate.py'
    )
    Run-Pytest 'bidirectional-50000-real-mcp' @('nexus/tests/test_bidirectional_50000.py') @{NEXUS_RUN_50K='1'}

    $report.status = 'PASS'
}
catch {
    $report.status = 'FAIL'
    $report.error = $_.Exception.Message
    throw
}
finally {
    $report.finished_utc = [DateTime]::UtcNow.ToString('o')
    Save-Report
    Write-Host ('NEXUS POST-INSTALL = ' + $report.status)
    Write-Host ('REPORT: ' + $reportPath)
    if ($report.legacy_accounts_present.Count -gt 0) {
        Write-Host ('LEGACY WINDOWS ACCOUNTS PRESENT, NOT USED: ' + ($report.legacy_accounts_present -join ', '))
    }
}
