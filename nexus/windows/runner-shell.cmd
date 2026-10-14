@echo off
setlocal DisableDelayedExpansion
rem Nexus Windows CMD Shell Runner. Only the Host may select a process.
rem Inputs are fixed positional values; no CALL, evaluation, pipes or expansion
rem of text from the Folha. AppContainer and Job are inherited from the Host.

if not "%~5"=="" exit /b 2
if /i "%~3"=="verify" goto dispatch
if /i "%~3"=="interpret" goto dispatch
if /i "%~3"=="proofread" goto dispatch
if /i "%~3"=="convert_pdf" goto dispatch
if /i "%~3"=="video" goto dispatch
if /i "%~3"=="podcast" goto dispatch
if /i "%~3"=="visual_podcast" goto dispatch
if /i "%~3"=="book" goto dispatch
if /i "%~3"=="music" goto dispatch
if /i "%~3"=="web" goto dispatch
exit /b 2

:dispatch
if not exist "%~1" exit /b 2
if not exist "%~2" exit /b 2
if /i not "%~nx4"=="input.bin" exit /b 2
"%~1" -I "%~2" "%~3" "%~4"
exit /b %ERRORLEVEL%
