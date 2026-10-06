@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo === NEXUS LOCAL - INSTALACAO COMPLETA ===
echo Este ficheiro instala o Nexus e as ferramentas fixadas no repositorio.
echo Nao cria contas Windows Nexus/NexusTool e nao pede passwords dessas contas.
echo.

if not exist ".\nexus\windows\install-nexus-complete.ps1" (
  echo FAIL: executa este BAT na raiz do repositorio Nexus.
  exit /b 2
)

where git.exe >nul 2>nul || (
  echo FAIL: Git nao encontrado. Instala Git e volta a executar.
  exit /b 3
)

for /f "delims=" %%i in ('git rev-parse --show-toplevel 2^>nul') do set "ROOT=%%i"
if not defined ROOT (
  echo FAIL: esta pasta nao e um repositorio Git.
  exit /b 4
)
if /I not "%ROOT%"=="%CD%" (
  echo FAIL: executa a partir da raiz oficial do repositorio.
  exit /b 5
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\nexus\windows\install-nexus-complete.ps1" -RepoRoot "%CD%" -ToolsRoot "C:\Nexus-Tools" -Device cuda -AuthorizeInstall
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo NEXUS INSTALACAO = FAIL
  echo Consulta C:\Nexus-Tools\complete-install-report.json
  exit /b %RC%
)

powershell.exe -NoProfile -Command "$p='C:\Nexus-Tools\complete-install-report.json'; if(-not(Test-Path -LiteralPath $p)){exit 20}; $r=Get-Content -LiteralPath $p -Raw|ConvertFrom-Json; if($r.status -ne 'PASS'){Write-Host ('INSTALL STATUS: '+$r.status); exit 21}; Write-Host ('INSTALL STATUS: PASS'); Write-Host ('NEXUS HEAD: '+$r.nexus_head); Write-Host ('LAUNCHER: '+$r.launcher.path)"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo NEXUS INSTALACAO = RELATORIO INVALIDO
  exit /b %RC%
)

echo.
echo NEXUS INSTALACAO = PASS
echo Agora executa TESTAR-NEXUS-POS-INSTALACAO.bat
exit /b 0
