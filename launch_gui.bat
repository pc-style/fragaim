@echo off
title Unibot GUI Launcher
echo Starting Unibot GUI...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Python is not installed or not in PATH
        echo Please install Python 3.8 or higher from https://python.org
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

REM Check if required packages are installed
echo Checking dependencies...
%PYTHON_CMD% -c "import tkinter, configparser, threading" >nul 2>&1
if errorlevel 1 (
    echo Error: Required Python packages are missing
    echo Installing required packages...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Launch the GUI
%PYTHON_CMD% launch_gui.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo An error occurred while running the GUI
    pause
)