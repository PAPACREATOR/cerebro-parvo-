@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
if not exist "nexus\windows\test-real-bidirectional.ps1" (
 echo NEXUS FAIL: actualizador de testes ausente nesta pasta.
 exit /b 2
)
where powershell.exe >nul 2>nul
if errorlevel 1 (
 echo NEXUS FAIL: PowerShell ausente.
 exit /b 2
)
echo NEXUS: testar o checkout existente, sem atualizar ou reinstalar.
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0nexus\windows\test-real-bidirectional.ps1"
set "RC=%ERRORLEVEL%"
echo NEXUS: consultar o relatorio indicado acima. Codigo=%RC%
exit /b %RC%
