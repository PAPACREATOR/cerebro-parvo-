# Nexus Windows Shell Runner.
# Only the Host selects the process and starts this script inside LPAC/Job.
# Never eval text supplied by Folha; all arguments remain separate values.
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true, Position=0)][string]$PythonExecutable,
  [Parameter(Mandatory=$true, Position=1)][string]$PythonAdapter,
  [Parameter(Mandatory=$true, Position=2)][string]$Process,
  [Parameter(Mandatory=$true, Position=3)][string]$InputPath
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$allowed = @(
  'verify','interpret','proofread','convert_pdf','video','podcast',
  'visual_podcast','book','music','web'
)
if ($allowed -cnotcontains $Process) {
  [Console]::Error.WriteLine('Nexus Shell: processo não autorizado.')
  exit 2
}
if (-not [System.IO.Path]::IsPathRooted($PythonExecutable) -or
    -not [System.IO.Path]::IsPathRooted($PythonAdapter) -or
    -not [System.IO.Path]::IsPathRooted($InputPath) -or
    [System.IO.Path]::GetFileName($InputPath) -cne 'input.bin') {
  [Console]::Error.WriteLine('Nexus Shell: argumentos inválidos.')
  exit 2
}
# PowerShell is a process launcher only. Python executes one pinned adapter
# inside the inherited Windows AppContainer and Job Object.
# stdout is reserved solely for the JSON envelope from that adapter.
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
& $PythonExecutable '-I' $PythonAdapter $Process $InputPath
$code = $LASTEXITCODE
if ($null -eq $code) { exit 2 }
exit [int]$code
