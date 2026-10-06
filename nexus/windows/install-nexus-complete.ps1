[CmdletBinding()]
param(
    [string]$RepoRoot = '',
    [string]$ToolsRoot = 'C:\Nexus-Tools',
    [ValidateSet('cuda','cpu')][string]$Device = 'cuda',
    [switch]$AuthorizeInstall
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not $AuthorizeInstall) {
    throw 'NEXUS_INSTALL_AUTHORIZATION_REQUIRED: rerun with -AuthorizeInstall only after explicit human approval.'
}
if ($env:OS -ne 'Windows_NT' -or -not [Environment]::Is64BitOperatingSystem) {
    throw 'NEXUS_WINDOWS_X64_REQUIRED'
}

$ExpectedOrigin = 'https://github.com/PAPACREATOR/cerebro-parvo-.git'
$OpenNotebookOrigin = 'https://github.com/lfnovo/open-notebook.git'
$OpenNotebookPin = '315d5255af2a5132aada41c94d5c3c5dc8e837aa'
$SpeachesOrigin = 'https://github.com/speaches-ai/speaches.git'
$SpeachesPin = '993994f7984bf3fe9655b267448328cf66fccb42'
$SurrealVersion = '2.7.0'
$SurrealSha256 = '55c7e05ee2b68ec0d8b86c4b588e9b9807f257af8c15c05d17074514c64d8c91'
$LanguageToolVersion = '6.6'
$LanguageToolSha256 = '53600506b399bb5ffe1e4c8dec794fd378212f14aaf38ccef9b6f89314d11631'
$PyInstallerVersion = '6.16.0'

function Invoke-Checked {
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [string[]]$Arguments = @(),
        [string]$WorkingDirectory = ''
    )
    $old = Get-Location
    try {
        if ($WorkingDirectory) { Set-Location -LiteralPath $WorkingDirectory }
        & $FilePath @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw ('NEXUS_COMMAND_FAILED: ' + $FilePath + ' exit=' + $LASTEXITCODE)
        }
    }
    finally {
        if ($WorkingDirectory) { Set-Location $old }
    }
}

function Refresh-ProcessPath {
    $machine = [Environment]::GetEnvironmentVariable('Path','Machine')
    $user = [Environment]::GetEnvironmentVariable('Path','User')
    $env:Path = @($machine,$user,$env:Path) -join ';'
}

function Resolve-Executable {
    param([string[]]$Names, [string[]]$Candidates = @())
    foreach ($name in $Names) {
        $cmd = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($cmd) { return $cmd.Source }
    }
    foreach ($candidate in $Candidates) {
        $matches = @(Get-ChildItem -Path $candidate -File -ErrorAction SilentlyContinue | Sort-Object FullName -Descending)
        if ($matches.Count -gt 0) { return $matches[0].FullName }
        if (Test-Path -LiteralPath $candidate) { return (Resolve-Path -LiteralPath $candidate).Path }
    }
    return $null
}

function Ensure-WingetPackage {
    param([Parameter(Mandatory=$true)][string]$Id)
    $winget = Resolve-Executable @('winget.exe')
    if (-not $winget) { throw 'NEXUS_WINGET_REQUIRED: install Microsoft App Installer first.' }
    $listed = & $winget list --id $Id --exact --accept-source-agreements 2>&1
    if ($LASTEXITCODE -ne 0 -or ("$listed" -notmatch [regex]::Escape($Id))) {
        & $winget install --id $Id --exact --source winget --silent --accept-package-agreements --accept-source-agreements --disable-interactivity
        if ($LASTEXITCODE -ne 0) { throw ('NEXUS_WINGET_INSTALL_FAILED: ' + $Id) }
    }
    Refresh-ProcessPath
}

function Install-PinnedRepo {
    param(
        [string]$Git,
        [string]$Origin,
        [string]$Pin,
        [string]$Destination
    )
    if (Test-Path -LiteralPath $Destination) {
        if (-not (Test-Path -LiteralPath (Join-Path $Destination '.git'))) {
            throw ('NEXUS_EXISTING_PATH_NOT_GIT: ' + $Destination)
        }
        $actualOrigin = (& $Git -C $Destination remote get-url origin).Trim()
        $head = (& $Git -C $Destination rev-parse HEAD).Trim()
        $dirty = & $Git -C $Destination status --porcelain
        if ($actualOrigin -ne $Origin) { throw ('NEXUS_WRONG_TOOL_ORIGIN: ' + $Destination) }
        if ($head -ne $Pin) {
            if ($dirty) { throw ('NEXUS_TOOL_DIRTY_REFUSING_CHECKOUT: ' + $Destination) }
            Invoke-Checked $Git @('-C',$Destination,'fetch','--depth','1','origin',$Pin)
            Invoke-Checked $Git @('-C',$Destination,'checkout','--detach',$Pin)
        }
    } else {
        Invoke-Checked $Git @('clone','--filter=blob:none',$Origin,$Destination)
        Invoke-Checked $Git @('-C',$Destination,'fetch','--depth','1','origin',$Pin)
        Invoke-Checked $Git @('-C',$Destination,'checkout','--detach',$Pin)
    }
    $actual = (& $Git -C $Destination rev-parse HEAD).Trim()
    if ($actual -ne $Pin) { throw ('NEXUS_PIN_MISMATCH: ' + $Destination) }
    return $actual
}

function Download-Verified {
    param([string]$Uri,[string]$Destination,[string]$Sha256)
    if (Test-Path -LiteralPath $Destination) {
        $existing = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($existing -eq $Sha256) { return $Destination }
        throw ('NEXUS_EXISTING_DOWNLOAD_HASH_MISMATCH: ' + $Destination)
    }
    Invoke-WebRequest -Uri $Uri -OutFile $Destination -UseBasicParsing
    $actual = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $Sha256) {
        Remove-Item -LiteralPath $Destination -Force
        throw ('NEXUS_DOWNLOAD_HASH_MISMATCH: ' + $Uri)
    }
    return $Destination
}

function Wait-Http {
    param([string]$Uri,[int]$Seconds = 60)
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 3
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) { return }
        } catch {}
        Start-Sleep -Milliseconds 500
    }
    throw ('NEXUS_HTTP_TIMEOUT: ' + $Uri)
}

function New-RandomHex {
    param([int]$Bytes = 32)
    $buffer = New-Object byte[] $Bytes
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($buffer) } finally { $rng.Dispose() }
    return -join ($buffer | ForEach-Object { $_.ToString('x2') })
}

if (-not $RepoRoot) {
    $RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot '.git'))) { throw 'NEXUS_REPOSITORY_NOT_FOUND' }

$bootstrapGit = Resolve-Executable @('git.exe','git')
if (-not $bootstrapGit) {
    Ensure-WingetPackage 'Git.Git'
    $bootstrapGit = Resolve-Executable @('git.exe','git') @("$env:ProgramFiles\Git\cmd\git.exe")
}
if (-not $bootstrapGit) { throw 'NEXUS_GIT_REQUIRED' }

$origin = (& $bootstrapGit -C $RepoRoot remote get-url origin).Trim()
if ($origin -ne $ExpectedOrigin) { throw 'NEXUS_WRONG_ORIGIN' }
$dirty = & $bootstrapGit -C $RepoRoot status --porcelain
if ($dirty) { throw 'NEXUS_DIRTY_TREE: preserve/commit local work before installation.' }
$NexusHead = (& $bootstrapGit -C $RepoRoot rev-parse HEAD).Trim()

$null = New-Item -ItemType Directory -Force -Path $ToolsRoot
$ToolsRoot = (Resolve-Path -LiteralPath $ToolsRoot).Path
$BinRoot = Join-Path $ToolsRoot 'bin'
$Downloads = Join-Path $ToolsRoot 'downloads'
$Models = Join-Path $ToolsRoot 'models'
$Logs = Join-Path $ToolsRoot 'logs'
$Build = Join-Path $ToolsRoot 'build'
foreach ($path in @($BinRoot,$Downloads,$Models,$Logs,$Build)) {
    $null = New-Item -ItemType Directory -Force -Path $path
}

$report = [ordered]@{
    schema = 'nexus.windows-complete-install.v1'
    status = 'RUNNING'
    started_utc = [DateTime]::UtcNow.ToString('o')
    finished_utc = $null
    nexus_head = $NexusHead
    repo_root = $RepoRoot
    tools_root = $ToolsRoot
    device = $Device
    prerequisites = [ordered]@{}
    tools = [ordered]@{}
    models = [ordered]@{}
    launcher = [ordered]@{}
    pending = @()
    error = $null
}
$reportPath = Join-Path $ToolsRoot 'complete-install-report.json'

function Save-Report {
    $report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $reportPath -Encoding UTF8
}

try {
    Save-Report

    # Common Windows dependencies. Every package is independently verified below.
    foreach ($id in @(
        'Git.Git',
        'Python.Python.3.12',
        'OpenJS.NodeJS.LTS',
        'Microsoft.OpenJDK.17',
        'TheDocumentFoundation.LibreOffice',
        'DigitalScholar.Zotero',
        'Gyan.FFmpeg',
        'astral-sh.uv',
        'Ollama.Ollama',
        'Microsoft.VCRedist.2015+.x64'
    )) {
        Ensure-WingetPackage $id
        $report.prerequisites[$id] = 'INSTALLED_OR_PRESENT'
        Save-Report
    }

    $git = Resolve-Executable @('git.exe','git') @("$env:ProgramFiles\Git\cmd\git.exe")
    $py = Resolve-Executable @('py.exe','py') @("$env:SystemRoot\py.exe")
    $node = Resolve-Executable @('node.exe','node') @("$env:ProgramFiles\nodejs\node.exe")
    $npm = Resolve-Executable @('npm.cmd','npm') @("$env:ProgramFiles\nodejs\npm.cmd")
    $java = Resolve-Executable @('java.exe','java') @("$env:ProgramFiles\Microsoft\jdk-17*\bin\java.exe")
    $soffice = Resolve-Executable @('soffice.com') @("$env:ProgramFiles\LibreOffice\program\soffice.com")
    $zotero = Resolve-Executable @('zotero.exe') @("$env:ProgramFiles\Zotero\zotero.exe","$([Environment]::GetFolderPath('ProgramFilesX86'))\Zotero\zotero.exe","$env:LOCALAPPDATA\Programs\Zotero\zotero.exe")
    $ffmpeg = Resolve-Executable @('ffmpeg.exe','ffmpeg')
    $ffprobe = Resolve-Executable @('ffprobe.exe','ffprobe')
    $uv = Resolve-Executable @('uv.exe','uv') @("$env:USERPROFILE\.local\bin\uv.exe","$env:LOCALAPPDATA\Microsoft\WinGet\Links\uv.exe")
    $ollama = Resolve-Executable @('ollama.exe','ollama') @("$env:LOCALAPPDATA\Programs\Ollama\ollama.exe")

    foreach ($pair in @(
        @('git',$git),@('py',$py),@('node',$node),@('npm',$npm),@('java',$java),
        @('libreoffice',$soffice),@('zotero',$zotero),@('ffmpeg',$ffmpeg),@('ffprobe',$ffprobe),
        @('uv',$uv),@('ollama',$ollama)
    )) {
        if (-not $pair[1] -or -not (Test-Path -LiteralPath $pair[1])) {
            throw ('NEXUS_REQUIRED_EXECUTABLE_MISSING: ' + $pair[0])
        }
        $report.tools[$pair[0]] = [ordered]@{ status='FOUND'; path=$pair[1] }
    }

    $python312 = (& $py -3.12 -c "import sys; assert sys.version_info[:2] == (3,12); print(sys.executable)").Trim()
    if (-not (Test-Path -LiteralPath $python312)) { throw 'NEXUS_PYTHON_312_NOT_RESOLVED' }
    $report.tools.python312 = [ordered]@{ status='PASS'; path=$python312; version=(& $python312 --version 2>&1 | Out-String).Trim() }
    $report.tools.git.version = (& $git --version | Out-String).Trim()
    $report.tools.node.version = (& $node --version | Out-String).Trim()
    $report.tools.java.version = (& $java -version 2>&1 | Select-Object -First 1 | Out-String).Trim()
    $report.tools.libreoffice.version = (& $soffice --version 2>&1 | Out-String).Trim()
    $report.tools.ffmpeg.version = (& $ffmpeg -version 2>&1 | Select-Object -First 1 | Out-String).Trim()
    $report.tools.zotero.version = (Get-Item -LiteralPath $zotero).VersionInfo.FileVersion
    Save-Report

    # Stable standalone LanguageTool 6.6, fixed checksum from the project release announcement.
    $ltZip = Join-Path $Downloads 'LanguageTool-6.6.zip'
    Download-Verified 'https://languagetool.org/download/LanguageTool-6.6.zip' $ltZip $LanguageToolSha256 | Out-Null
    $ltRoot = Join-Path $ToolsRoot 'LanguageTool'
    if (-not (Test-Path -LiteralPath $ltRoot)) {
        $null = New-Item -ItemType Directory -Path $ltRoot
        Expand-Archive -LiteralPath $ltZip -DestinationPath $ltRoot
    }
    $ltJar = Get-ChildItem -LiteralPath $ltRoot -Filter 'languagetool-commandline.jar' -File -Recurse | Select-Object -First 1
    if (-not $ltJar) { throw 'NEXUS_LANGUAGETOOL_JAR_MISSING' }
    Invoke-Checked $java @('-jar',$ltJar.FullName,'--version')
    $report.tools.languagetool = [ordered]@{
        status='INSTALLED_TESTED'; version=$LanguageToolVersion; jar=$ltJar.FullName; archive_sha256=$LanguageToolSha256
    }
    Save-Report

    # SurrealDB 2.7.0 is pinned because this is the version already exercised with the Nexus/OpenNotebook lab.
    $surreal = Join-Path $BinRoot 'surreal.exe'
    Download-Verified 'https://github.com/surrealdb/surrealdb/releases/download/v2.7.0/surreal-v2.7.0.windows-amd64.exe' $surreal $SurrealSha256 | Out-Null
    $surrealVersionText = (& $surreal version 2>&1 | Out-String).Trim()
    if ($surrealVersionText -notmatch '2\.7\.0') { throw 'NEXUS_SURREAL_VERSION_MISMATCH' }
    $report.tools.surrealdb = [ordered]@{ status='INSTALLED_TESTED'; version=$surrealVersionText; path=$surreal; sha256=$SurrealSha256 }
    Save-Report

    # Open Notebook source is pinned. Data remains separate from Nexus Canonical/Creative.
    $openNotebook = Join-Path $ToolsRoot 'OpenNotebook'
    $openHead = Install-PinnedRepo $git $OpenNotebookOrigin $OpenNotebookPin $openNotebook
    Invoke-Checked $uv @('sync','--frozen') $openNotebook
    Invoke-Checked $npm @('ci') (Join-Path $openNotebook 'frontend')
    Invoke-Checked $npm @('run','build') (Join-Path $openNotebook 'frontend')
    $openPython = Join-Path $openNotebook '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $openPython)) { throw 'NEXUS_OPEN_NOTEBOOK_VENV_MISSING' }

    $openEnv = Join-Path $openNotebook '.env'
    if (-not (Test-Path -LiteralPath $openEnv)) {
        $dbPassword = New-RandomHex 24
        $encryptionKey = New-RandomHex 32
        $apiPassword = New-RandomHex 24
        @(
            'SURREAL_URL=ws://127.0.0.1:8000/rpc',
            'SURREAL_USER=root',
            ('SURREAL_PASSWORD=' + $dbPassword),
            'SURREAL_NAMESPACE=open_notebook',
            'SURREAL_DATABASE=open_notebook',
            ('OPEN_NOTEBOOK_ENCRYPTION_KEY=' + $encryptionKey),
            ('OPEN_NOTEBOOK_PASSWORD=' + $apiPassword),
            'OPEN_NOTEBOOK_WORKER_MAX_TASKS=1'
        ) | Set-Content -LiteralPath $openEnv -Encoding UTF8
    }
    $report.tools.open_notebook = [ordered]@{
        status='INSTALLED_BUILT'; path=$openNotebook; commit=$openHead; version='1.15.0'; env=$openEnv
    }
    Save-Report

    # Local LLM and embeddings used later by Open Notebook. Do not expose Ollama outside loopback.
    try { Invoke-WebRequest -Uri 'http://127.0.0.1:11434/api/tags' -UseBasicParsing -TimeoutSec 2 | Out-Null }
    catch {
        Start-Process -FilePath $ollama -ArgumentList @('serve') -WindowStyle Hidden | Out-Null
        Wait-Http 'http://127.0.0.1:11434/api/tags' 60
    }
    Invoke-Checked $ollama @('pull','qwen3:4b')
    Invoke-Checked $ollama @('pull','nomic-embed-text')
    $ollamaList = (& $ollama list | Out-String)
    if ($ollamaList -notmatch 'qwen3:4b' -or $ollamaList -notmatch 'nomic-embed-text') {
        throw 'NEXUS_OLLAMA_MODELS_MISSING'
    }
    $report.models.ollama = [ordered]@{ status='INSTALLED_TESTED'; language='qwen3:4b'; embedding='nomic-embed-text' }
    Save-Report

    # Local TTS server for podcast audio, pinned to an observed upstream commit.
    $speaches = Join-Path $ToolsRoot 'Speaches'
    $speachesHead = Install-PinnedRepo $git $SpeachesOrigin $SpeachesPin $speaches
    Invoke-Checked $uv @('sync','--frozen') $speaches
    $speachesOut = Join-Path $Logs 'speaches-install.stdout.txt'
    $speachesErr = Join-Path $Logs 'speaches-install.stderr.txt'
    $speachesProcess = Start-Process -FilePath $uv -ArgumentList @(
        'run','uvicorn','--factory','--host','127.0.0.1','--port','8969','speaches.main:create_app'
    ) -WorkingDirectory $speaches -RedirectStandardOutput $speachesOut -RedirectStandardError $speachesErr -PassThru -WindowStyle Hidden
    try {
        Wait-Http 'http://127.0.0.1:8969/v1/models' 120
        $oldSpeaches = $env:SPEACHES_BASE_URL
        $env:SPEACHES_BASE_URL = 'http://127.0.0.1:8969'
        try {
            Invoke-Checked $uv @('run','speaches-cli','model','download','speaches-ai/Kokoro-82M-v1.0-ONNX') $speaches
        }
        finally {
            $env:SPEACHES_BASE_URL = $oldSpeaches
        }
    }
    finally {
        if ($speachesProcess -and -not $speachesProcess.HasExited) {
            Stop-Process -Id $speachesProcess.Id -Force -ErrorAction SilentlyContinue
            $speachesProcess.WaitForExit()
        }
    }
    $speachesLauncher = Join-Path $BinRoot 'Start-Speaches-Nexus.cmd'
    @"
@echo off
setlocal
cd /d "$speaches"
"$uv" run uvicorn --factory --host 127.0.0.1 --port 8969 speaches.main:create_app
endlocal
"@ | Set-Content -LiteralPath $speachesLauncher -Encoding ASCII
    $report.tools.speaches = [ordered]@{ status='INSTALLED_TESTED'; path=$speaches; commit=$speachesHead; endpoint='http://127.0.0.1:8969'; launcher=$speachesLauncher }
    $report.models.kokoro = [ordered]@{ status='DOWNLOADED'; id='speaches-ai/Kokoro-82M-v1.0-ONNX' }
    Save-Report

    # ACE-Step and Forge use the already reviewed, explicitly authorized installer.
    $mediaInstaller = Join-Path $RepoRoot 'nexus\windows\install-media-tools.ps1'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $mediaInstaller -ToolsRoot $ToolsRoot -AuthorizeInstall
    if ($LASTEXITCODE -ne 0) { throw 'NEXUS_MEDIA_INSTALL_FAILED' }

    # Pre-fetch the ACE-Step main model so the later real-music test cannot hide a first-use download.
    $ace = Join-Path $ToolsRoot 'ACE-Step-1.5'
    $aceModels = Join-Path $Models 'ace-step'
    $oldAceModels = $env:ACESTEP_CHECKPOINTS_DIR
    $env:ACESTEP_CHECKPOINTS_DIR = $aceModels
    try {
        $code = "from acestep.model_downloader import ensure_main_model; ok,msg=ensure_main_model(); print(msg); raise SystemExit(0 if ok else 1)"
        Invoke-Checked $uv @('run','--no-sync','python','-c',$code) $ace
    }
    finally {
        $env:ACESTEP_CHECKPOINTS_DIR = $oldAceModels
    }
    if (-not (Test-Path -LiteralPath (Join-Path $aceModels 'acestep-v15-turbo'))) {
        throw 'NEXUS_ACE_MAIN_MODEL_MISSING'
    }
    $report.models.ace_step = [ordered]@{ status='DOWNLOADED'; model='acestep-v15-turbo'; root=$aceModels }
    $report.tools.forge = [ordered]@{
        status='RUNTIME_INSTALLED'; path=(Join-Path $ToolsRoot 'Forge'); model='NOT_SELECTED';
        note='No image checkpoint was silently chosen because model licences/size are separate decisions.'
    }
    Save-Report

    # Add the already reviewed avatar extension and its pinned Wav2Lip/SFD weights.
    $avatarInstaller = Join-Path $RepoRoot 'nexus\lab\open_notebook_avatar\install-windows.ps1'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $avatarInstaller -OpenNotebookRoot $openNotebook -ApiPython $openPython -Device $Device -AuthorizeInstall
    if ($LASTEXITCODE -ne 0) { throw 'NEXUS_AVATAR_INSTALL_FAILED' }
    $avatarModels = Join-Path $openNotebook 'data\avatar-models'
    foreach ($name in @('wav2lip.pth','s3fd.pth')) {
        if (-not (Test-Path -LiteralPath (Join-Path $avatarModels $name))) { throw ('NEXUS_AVATAR_MODEL_MISSING: ' + $name) }
    }
    $report.models.avatar = [ordered]@{ status='DOWNLOADED'; root=$avatarModels; device=$Device }
    Save-Report

    # Configure deterministic Nexus adapters. OpenNotebook model/transformation IDs are intentionally
    # not invented here; later acceptance must bind real IDs and prove them.
    $runtime = Join-Path $RepoRoot 'nexus\runtime'
    $null = New-Item -ItemType Directory -Force -Path $runtime
    @{ java=$java; jar=$ltJar.FullName } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtime 'languagetool.json') -Encoding UTF8
    @{ executable=$soffice } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtime 'libreoffice.json') -Encoding UTF8
    $report.pending += 'OPEN_NOTEBOOK_MODEL_AND_TRANSFORMATION_BINDING'
    $report.pending += 'FORGE_IMAGE_CHECKPOINT_SELECTION'
    Save-Report

    # Run the existing Windows core/regression/security preparation after installation.
    $prepare = Join-Path $RepoRoot 'nexus\windows\prepare-nexus-core.ps1'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $prepare -RepoRoot $RepoRoot -ToolsRoot $ToolsRoot
    if ($LASTEXITCODE -ne 0) { throw 'NEXUS_CORE_PREPARE_AFTER_INSTALL_FAILED' }
    $nexusPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $nexusPython)) { throw 'NEXUS_VENV_MISSING_AFTER_PREPARE' }

    # Build a thin launcher EXE only. Kernel and sandbox remain normal Python files/runtime.
    $launcherVenv = Join-Path $Build 'launcher-venv'
    $launcherPython = Join-Path $launcherVenv 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $launcherPython)) {
        Invoke-Checked $python312 @('-m','venv',$launcherVenv)
    }
    Invoke-Checked $launcherPython @('-m','pip','install','--disable-pip-version-check',('pyinstaller==' + $PyInstallerVersion))
    $launcherSource = Join-Path $RepoRoot 'nexus\windows\nexus-launcher.py'
    $dist = Join-Path $Build 'dist'
    $work = Join-Path $Build 'pyinstaller-work'
    $spec = Join-Path $Build 'pyinstaller-spec'
    foreach ($dir in @($dist,$work,$spec)) { $null = New-Item -ItemType Directory -Force -Path $dir }
    Invoke-Checked $launcherPython @(
        '-m','PyInstaller','--clean','--noconfirm','--onefile','--noconsole',
        '--name','Nexus','--distpath',$dist,'--workpath',$work,'--specpath',$spec,$launcherSource
    )
    $builtExe = Join-Path $dist 'Nexus.exe'
    if (-not (Test-Path -LiteralPath $builtExe)) { throw 'NEXUS_EXE_BUILD_MISSING' }
    $finalExe = Join-Path $BinRoot 'Nexus.exe'
    Copy-Item -LiteralPath $builtExe -Destination $finalExe -Force
    $launcherConfig = [ordered]@{
        repo_root = $RepoRoot
        python = $nexusPython
        git = $git
        data_root = $runtime
        expected_origin = $ExpectedOrigin
    }
    $launcherConfig | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $BinRoot 'nexus-launcher.json') -Encoding UTF8
    $exeHash = (Get-FileHash -LiteralPath $finalExe -Algorithm SHA256).Hash.ToLowerInvariant()
    $report.launcher = [ordered]@{
        status='BUILT'; path=$finalExe; sha256=$exeHash; pyinstaller=$PyInstallerVersion;
        type='thin launcher; Kernel remains external validated Python runtime'
    }

    $report.status = if ($report.pending.Count -eq 0) { 'PASS' } else { 'PASS_WITH_EXPLICIT_PENDING_BINDINGS' }
}
catch {
    $report.status = 'FAIL'
    $report.error = $_.Exception.Message
    throw
}
finally {
    $report.finished_utc = [DateTime]::UtcNow.ToString('o')
    Save-Report
    Write-Host ('NEXUS COMPLETE INSTALL = ' + $report.status)
    Write-Host ('REPORT: ' + $reportPath)
    if ($report.pending.Count -gt 0) { Write-Host ('PENDING: ' + ($report.pending -join ', ')) }
}
