@echo off
TITLE Centaur Dental Clinic OS - 24/7 Live Production Service
echo =================================================================
echo   🚀 LAUNCHING CENTAUR CLINIC 24/7 LIVE PRODUCTION SERVICE
echo   Client Status: ACTIVE PAID SUBSCRIBER (₹36,000 + ₹6,000/mo)
echo =================================================================
echo.

REM Activate Virtual Environment
call .venv\Scripts\activate.bat

REM Launch Webhook Server in Background
start /B python webhook_server.py > webhook_server.log 2>&1

REM Launch Live Production Coordinator
python production_service.py

pause
