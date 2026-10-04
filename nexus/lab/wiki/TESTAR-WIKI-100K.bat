@echo off
setlocal
python "%~dp0test_web_research_wiki_100k.py" %*
exit /b %ERRORLEVEL%
