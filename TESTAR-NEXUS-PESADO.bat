@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "REPORT_DIR=nexus\lab\evidence\heavy-bat"
if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%"

echo ============================================================
echo NEXUS HEAVY LAB - MCP / SPIFF / CONDUCTOR / WINDOWS
echo ============================================================
echo.

set FAIL=0

call :run "01_compare_stack" python -m pytest nexus/tests/test_spiff_vs_conductor_500.py -q -s -o pythonpath=.
call :run "02_reverse_flow" python -m pytest nexus/tests/test_reverse_flow.py -q -s -o pythonpath=.
call :run "03_workflows" python -m pytest nexus/tests/test_workflows.py -q -s -o pythonpath=.
call :run "04_conductor" python -m pytest nexus/tests/test_conductor.py -q -s -o pythonpath=.
call :run "05_notebook" python -m pytest nexus/tests/test_notebook.py -q -s -o pythonpath=.
call :run "06_kernel_crash" python -m pytest nexus/tests/test_kernel_crash_contract.py -q -s -o pythonpath=.
call :run "07_practical_boundaries" python -m pytest nexus/tests/test_lab_practical_boundaries.py -q -s -o pythonpath=.
call :run "08_joint_5000" python -m pytest nexus/tests/test_spiff_conductor_bidirectional_5000.py -q -s -o pythonpath=.
call :run "09_all_nexus" python -m pytest nexus/tests -q -o pythonpath=.

echo.
echo ============================================================
if "%FAIL%"=="0" (
  echo NEXUS HEAVY LAB RESULT: PASS
) else (
  echo NEXUS HEAVY LAB RESULT: FAIL
)
echo Reports: %REPORT_DIR%
echo ============================================================
exit /b %FAIL%

:run
set "NAME=%~1"
shift
echo.
echo ------------------------------------------------------------
echo RUNNING: %NAME%
echo ------------------------------------------------------------
set "CMDLINE="
:build_cmd
if "%~1"=="" goto exec_cmd
if defined CMDLINE (
  set "CMDLINE=!CMDLINE! %1"
) else (
  set "CMDLINE=%1"
)
shift
goto build_cmd

:exec_cmd
call !CMDLINE! > "%REPORT_DIR%\%NAME%.log" 2>&1
set RC=!ERRORLEVEL!
type "%REPORT_DIR%\%NAME%.log"
if not "!RC!"=="0" (
  echo RESULT %NAME%: FAIL ^(!RC!^)
  set FAIL=1
) else (
  echo RESULT %NAME%: PASS
)
exit /b 0
