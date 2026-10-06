@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo === NEXUS LOCAL - TESTES POS-INSTALACAO ===
echo Testa a instalacao real, seguranca, fluxos deterministas e stress.
echo Nao promove nem escreve diretamente no Canonical.
echo.

if not exist ".\nexus\windows\test-post-install.ps1" (
  echo FAIL: executa este BAT na raiz do repositorio Nexus.
  exit /b 2
)
if not exist "C:\Nexus-Tools\complete-install-report.json" (
  echo FAIL: instalacao completa nao encontrada. Executa primeiro INSTALAR-NEXUS-COMPLETO.bat
  exit /b 3
)
if not exist ".\.venv\Scripts\python.exe" (
  echo FAIL: ambiente Python Nexus nao encontrado. Repete a instalacao.
  exit /b 4
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\nexus\windows\test-post-install.ps1" -RepoRoot "%CD%" -ToolsRoot "C:\Nexus-Tools"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo NEXUS POS-INSTALACAO = PASS
) else (
  echo NEXUS POS-INSTALACAO = FAIL
)
echo Relatorio: C:\Nexus-Tools\post-install-acceptance-report.json
exit /b %RC%
