[CmdletBinding()]
param(
    [string]$RepoRoot = '',
    [string]$ToolsRoot = 'C:\Nexus-Tools',
    [string]$Branch = 'lab-open-notebook-avatar-20261004'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Invoke-PowerShellChecked {
    param(
        [Parameter(Mandatory=$true)][string]$ScriptPath,
        [Parameter(Mandatory=$false)][string[]]$Arguments = @()
    )
    if (-not (Test-Path -LiteralPath $ScriptPath)) {
        throw ('NEXUS_SCRIPT_NOT_FOUND: ' + $ScriptPath)
    }
    & powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $ScriptPath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw ('NEXUS_STEP_FAILED: ' + (Split-Path $ScriptPath -Leaf))
    }
}

$repoFromScript = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$sync = Join-Path $PSScriptRoot 'sync-nexus-code.ps1'

$syncArgs = @('-Branch',$Branch)
if ($RepoRoot) {
    $syncArgs += @('-RepoRoot',$RepoRoot)
}
Invoke-PowerShellChecked -ScriptPath $sync -Arguments $syncArgs

# After sync, resolve the authoritative checkout. If -RepoRoot was omitted,
# the script's own checkout is the only location this wrapper is allowed to use.
if ($RepoRoot) {
    $RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
} else {
    $RepoRoot = (Resolve-Path -LiteralPath $repoFromScript).Path
}

$prepare = Join-Path $RepoRoot 'nexus\windows\prepare-nexus-core.ps1'
Invoke-PowerShellChecked -ScriptPath $prepare -Arguments @('-RepoRoot',$RepoRoot,'-ToolsRoot',$ToolsRoot)

$inventory = Join-Path $RepoRoot 'nexus\windows\inventory-external-tools.ps1'
Invoke-PowerShellChecked -ScriptPath $inventory -Arguments @('-ToolsRoot',$ToolsRoot)

$git = (Get-Command git.exe -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$head = (& $git -C $RepoRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'NEXUS_HEAD_READ_FAILED' }

$inventoryReport = Join-Path $ToolsRoot 'external-tools-inventory.json'
if (-not (Test-Path -LiteralPath $inventoryReport)) {
    throw 'NEXUS_EXTERNAL_INVENTORY_MISSING'
}

$coreReport = Join-Path $ToolsRoot 'pc-core-report.json'
if (-not (Test-Path -LiteralPath $coreReport)) {
    throw 'NEXUS_CORE_REPORT_MISSING'
}
$core = Get-Content -LiteralPath $coreReport -Raw | ConvertFrom-Json
if ($core.status -ne 'PASS' -or $core.head -ne $head) {
    throw 'NEXUS_CORE_REPORT_MISMATCH'
}

$report = [ordered]@{
    schema = 'nexus.local-bootstrap.v1'
    status = 'PASS'
    checked_utc = [DateTime]::UtcNow.ToString('o')
    repository = $RepoRoot
    branch = $Branch
    head = $head
    core_report = $coreReport
    external_inventory = $inventoryReport
    external_provisioning = 'BLOCKED_BY_POLICY'
    note = 'Code synchronized and Nexus core prepared/tested. Protected external provisioning was not bypassed.'
}
$reportPath = Join-Path $ToolsRoot 'local-bootstrap-report.json'
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8

Write-Host 'NEXUS LOCAL BOOTSTRAP = PASS'
Write-Host ('HEAD: ' + $head)
Write-Host ('REPORT: ' + $reportPath)
Write-Host 'External provisioning remains BLOCKED_BY_POLICY.'
