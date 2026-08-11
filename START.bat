@echo off
title AMAZEBOT - A Teenager Innovation
color 0B
echo.
echo  ==========================================
echo     AMAZEBOT - A Teenager Innovation
echo     Tribute to Suman Dutta sir
echo  ==========================================
echo.
echo  Project Members:
echo  G Venugopalan, Mahalakshmi R,
echo  Ram Eswar, Sleva Vignesh
echo  ==========================================
echo.

REM Try Python 3 first
python --version >nul 2>&1
if not errorlevel 1 (
    echo  Starting server with Python...
    echo.
    echo  Opening AMAZEBOT at:
    echo  http://localhost:8080/static/index.html
    echo.
    echo  Press Ctrl+C to stop the server.
    echo.
    start "" "http://localhost:8080/static/index.html"
    python -m http.server 8080
    pause
    exit /b
)

REM Try Python3 command
python3 --version >nul 2>&1
if not errorlevel 1 (
    echo  Starting server with Python3...
    echo.
    echo  Opening AMAZEBOT at:
    echo  http://localhost:8080/static/index.html
    echo.
    start "" "http://localhost:8080/static/index.html"
    python3 -m http.server 8080
    pause
    exit /b
)

REM Try Node.js / npx
npx --version >nul 2>&1
if not errorlevel 1 (
    echo  Starting server with Node.js...
    echo.
    start "" "http://localhost:3000"
    npx serve static -p 3000
    pause
    exit /b
)

REM Nothing found
echo  ==========================================
echo  ERROR: Python or Node.js not found!
echo  ==========================================
echo.
echo  Please install one of these:
echo.
echo  Python (recommended):
echo  https://www.python.org/downloads/
echo.
echo  Node.js:
echo  https://nodejs.org/
echo.
echo  OR use VS Code with Live Server extension
echo  and right-click static/index.html
echo  ==========================================
echo.
pause
