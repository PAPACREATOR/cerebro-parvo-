[CmdletBinding()]
param(
    [string]$RepoRoot = '',
    [string]$Branch = 'lab-open-notebook-avatar-20261004'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Resolve-NexusRepo {
    param([string]$Requested)
    $candidates = @()
    if ($Requested) { $candidates += $Requested }
    $candidates += @(
        (Get-Location).Path,
        'C:\Nexos',
        'C:\Nexus',
        'C:\work\nexus-publicacao',
        (Join-Path $env:USERPROFILE 'Desktop\cerebro-parvo-'),
        (Join-Path $env:USERPROFILE 'Documents\cerebro-parvo-'),
        (Join-Path $env:USERPROFILE 'Downloads\cerebro-parvo-')
    )
    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (-not $candidate) { continue }
        $gitDir = Join-Path $candidate '.git'
        if (Test-Path -LiteralPath $gitDir) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    throw 'NEXUS_REPOSITORY_NOT_FOUND: indica -RepoRoot com a pasta que contém .git.'
}

function Invoke-GitChecked {
    param([string[]]$Arguments, [string]$WorkingDirectory)
    & $script:Git -C $WorkingDirectory @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw ('Git falhou: ' + ($Arguments -join ' '))
    }
}

$RepoRoot = Resolve-NexusRepo -Requested $RepoRoot
$Git = (Get-Command git.exe -CommandType Application -ErrorAction Stop).Source

$origin = (& $Git -C $RepoRoot config --get remote.origin.url).Trim()
if ($LASTEXITCODE -ne 0 -or $origin -notmatch '^https://github\.com/PAPACREATOR/cerebro-parvo-\.git
    throw 'NEXUS_WRONG_ORIGIN: o checkout não aponta para PAPACREATOR/cerebro-parvo-.'
}

$dirty = & $Git -C $RepoRoot status --porcelain
if ($LASTEXITCODE -ne 0) { throw 'NEXUS_GIT_STATUS_FAILED' }
if ($dirty) {
    throw 'NEXUS_DIRTY_TREE: existem alterações locais; nada foi atualizado.'
}

Invoke-GitChecked -Arguments @('fetch','--prune','origin',$Branch) -WorkingDirectory $RepoRoot

& $Git -C $RepoRoot show-ref --verify --quiet "refs/heads/$Branch"
$localExists = ($LASTEXITCODE -eq 0)
if ($localExists) {
    Invoke-GitChecked -Arguments @('switch',$Branch) -WorkingDirectory $RepoRoot
}
else {
    Invoke-GitChecked -Arguments @('switch','--track','-c',$Branch,"origin/$Branch") -WorkingDirectory $RepoRoot
}

Invoke-GitChecked -Arguments @('merge','--ff-only',"origin/$Branch") -WorkingDirectory $RepoRoot

$head = (& $Git -C $RepoRoot rev-parse HEAD).Trim()
$remote = (& $Git -C $RepoRoot rev-parse "origin/$Branch").Trim()
if ($LASTEXITCODE -ne 0 -or $head -ne $remote) {
    throw 'NEXUS_SYNC_MISMATCH: HEAD local não corresponde ao remoto.'
}

Write-Host 'NEXUS CODE SYNC = PASS'
Write-Host ('REPO: ' + $RepoRoot)
Write-Host ('BRANCH: ' + $Branch)
Write-Host ('HEAD: ' + $head)
Write-Host 'Provisioning/instalação não foi executado.'
) {
    throw 'NEXUS_WRONG_ORIGIN: o checkout não aponta para PAPACREATOR/cerebro-parvo-.'
}

$dirty = & $Git -C $RepoRoot status --porcelain
if ($LASTEXITCODE -ne 0) { throw 'NEXUS_GIT_STATUS_FAILED' }
if ($dirty) {
    throw 'NEXUS_DIRTY_TREE: existem alterações locais; nada foi atualizado.'
}

Invoke-GitChecked -Arguments @('fetch','--prune','origin',$Branch) -WorkingDirectory $RepoRoot

& $Git -C $RepoRoot show-ref --verify --quiet "refs/heads/$Branch"
$localExists = ($LASTEXITCODE -eq 0)
if ($localExists) {
    Invoke-GitChecked -Arguments @('switch',$Branch) -WorkingDirectory $RepoRoot
}
else {
    Invoke-GitChecked -Arguments @('switch','--track','-c',$Branch,"origin/$Branch") -WorkingDirectory $RepoRoot
}

Invoke-GitChecked -Arguments @('merge','--ff-only',"origin/$Branch") -WorkingDirectory $RepoRoot

$head = (& $Git -C $RepoRoot rev-parse HEAD).Trim()
$remote = (& $Git -C $RepoRoot rev-parse "origin/$Branch").Trim()
if ($LASTEXITCODE -ne 0 -or $head -ne $remote) {
    throw 'NEXUS_SYNC_MISMATCH: HEAD local não corresponde ao remoto.'
}

Write-Host 'NEXUS CODE SYNC = PASS'
Write-Host ('REPO: ' + $RepoRoot)
Write-Host ('BRANCH: ' + $Branch)
Write-Host ('HEAD: ' + $head)
Write-Host 'Provisioning/instalação não foi executado.'
