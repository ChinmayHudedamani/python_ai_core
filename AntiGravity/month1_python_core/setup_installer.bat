@echo off
TITLE Centaur Dental Clinic OS - 1-Click Desktop Installer
echo =================================================================
echo   🏥 LAUNCHING CENTAUR CLINIC AUTOMATED DESKTOP INSTALLER
echo =================================================================
echo.

REM 1. Create Virtual Environment if missing
if not exist ".venv" (
    echo [1/4] Creating local Python virtual environment...
    python -m venv .venv
)

REM 2. Activate Virtual Environment & Install Dependencies
echo [2/4] Installing dependencies (google-genai, python-dotenv)...
call .venv\Scripts\activate.bat
pip install google-genai python-dotenv > nul 2>&1

REM 3. Run Custom Clinic Onboarding Configurator
echo [3/4] Running Custom Clinic Onboarding Wizard...
python clinic_onboarding.py

REM 4. Launch Sales Demo / Centaur System
echo [4/4] Starting Centaur Clinic Assistant...
echo.
python demo.py

pause
