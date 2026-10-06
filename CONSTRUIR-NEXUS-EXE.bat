@echo off
setlocal
cd /d "%~dp0"

echo === NEXUS - PREPARAR WINDOWS E CONSTRUIR EXE ===
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\nexus\windows\prepare-nexus-core.ps1" -RepoRoot "%CD%"
if errorlevel 1 (
  echo.
  echo NEXUS EXE = NAO CONSTRUIDO: a preparacao/testes falharam.
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\nexus\windows\build-nexus-launcher.ps1" -RepoRoot "%CD%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo NEXUS EXE = PASS
  echo Duplo clique em Nexus.exe para abrir a Folha.
) else (
  echo NEXUS EXE = FAIL
)
exit /b %RC%
