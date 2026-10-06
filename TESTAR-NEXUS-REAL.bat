@echo off
setlocal
cd /d "%~dp0"

echo === NEXUS - TESTES REAIS WINDOWS ===
echo.
echo Este BAT executa:
echo - ataques ao Human Gate / Canonical
echo - documento livro em LibreOffice real
echo - pesquisa Zotero local
echo - pesquisa Internet real
echo - musica ACE-Step real
echo - podcast OpenNotebook real
echo - podcast visual real, se NEXUS_AVATAR_NAME estiver configurado
echo.
echo Saidas externas ficam em C:\Nexus-Tools\reports e NAO entram em Canonical.
echo.

echo A validar primeiro o HEAD completo e os limites de seguranca...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\nexus\windows\prepare-nexus-core.ps1" -RepoRoot "%CD%"
if errorlevel 1 (
  echo NEXUS TESTES REAIS = BLOQUEADO: regressao/security gate falhou.
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\nexus\windows\test-real-acceptance.ps1" -RepoRoot "%CD%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo NEXUS TESTES REAIS = PASS FISICO
  echo ATENCAO: media, Zotero e web ainda precisam de entrar no Host/Creative/Human Gate para o E2E final.
) else if "%RC%"=="2" (
  echo NEXUS TESTES REAIS = INCOMPLETO
  echo Ver o summary.json para saber o que falta configurar ou integrar.
) else (
  echo NEXUS TESTES REAIS = FAIL
  echo Ver o summary.json e os logs antes de alterar qualquer versao.
)
exit /b %RC%
