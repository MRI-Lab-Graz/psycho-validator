@echo off
::
:: Windows launcher for Psycho-Validator Web Interface
:: Double-click this file to start the web interface
::

title Psycho-Validator Web Interface

echo.
echo ==========================================
echo    Psycho-Validator Web Interface
echo ==========================================
echo.

:: Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    if not exist ".venv\bin\activate" (
        echo ❌ Virtual environment not found
        echo    Please run setup.sh or scripts\setup-windows.bat first
        echo.
        pause
        exit /b 1
    )
)

:: Activate virtual environment (Windows style)
if exist ".venv\Scripts\activate.bat" (
    echo 🔌 Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo ❌ Cannot activate virtual environment
    echo    Windows activation script not found
    pause
    exit /b 1
)

:: Check if Flask is installed
python -c "import flask" >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Flask not installed, installing now...
    pip install Flask Werkzeug
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Flask
        pause
        exit /b 1
    )
)

:: Start the web interface
echo.
echo 🚀 Starting web interface...
echo 🔗 Your browser should open automatically
echo 💡 If not, open: http://127.0.0.1:5000
echo.
echo ⚠️  To stop the server, close this window or press Ctrl+C
echo.

python launch_web.py

echo.
echo 👋 Web interface stopped
pause