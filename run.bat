@echo off
rem Double-click this file to start the app (it works from any folder).
cd /d "%~dp0"
python app.py
if errorlevel 1 (
    py app.py
    if errorlevel 1 (
        echo.
        echo Could not start. Make sure Python is installed from python.org
        echo with "Add Python to PATH" ticked.
        pause
    )
)
