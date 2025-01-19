@echo off
cd /d "%~dp0"
if not exist "venv" (
    >nul 2>&1 echo Creating virtual environment...
    >nul 2>&1 python -m venv venv
    >nul 2>&1 call venv\Scripts\activate
    >nul 2>&1 echo Installing requirements...
    pip install -r requirements.txt || (
        echo Error installing requirements
        pause
        exit /b 1
    )
) else (
    >nul 2>&1 call venv\Scripts\activate
)
start /b "" pythonw soundladder.py || (
    echo Error running soundladder.py
    pause
    exit /b 1
)
exit 