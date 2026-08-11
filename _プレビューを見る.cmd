@echo off
REM Preview the redesigned D-studyLab top page (NOT published).
REM Starts a local web server in this folder and opens the browser.
setlocal
cd /d "%~dp0"
set PORT=8799
echo.
echo   D-studyLab - preview (local only, nothing is published)
echo   http://127.0.0.1:%PORT%/
echo.
echo   Close this window to stop the preview.
echo.
start "" "http://127.0.0.1:%PORT%/"
python -m http.server %PORT% --bind 127.0.0.1
