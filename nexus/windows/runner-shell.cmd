@echo off
setlocal DisableDelayedExpansion
rem Nexus Host-owned Windows Shell dispatcher, not a tool executor.
rem One registered process ID only. Never read or execute Folha text.
rem Host validates stdout byte-for-byte and runs the worker separately in LPAC.
if not "%~2"=="" exit /b 2
if /i "%~1"=="verify" goto dispatch
if /i "%~1"=="interpret" goto dispatch
if /i "%~1"=="proofread" goto dispatch
if /i "%~1"=="convert_pdf" goto dispatch
if /i "%~1"=="video" goto dispatch
if /i "%~1"=="podcast" goto dispatch
if /i "%~1"=="visual_podcast" goto dispatch
if /i "%~1"=="book" goto dispatch
if /i "%~1"=="music" goto dispatch
if /i "%~1"=="web" goto dispatch
exit /b 2

:dispatch
echo NEXUS_SHELL_READY:%~1
exit /b 0
