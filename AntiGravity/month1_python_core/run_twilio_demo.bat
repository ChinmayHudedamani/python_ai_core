@echo off
TITLE Centaur Dental Clinic OS - Live Twilio WhatsApp Sandbox
echo =================================================================
echo   📱 LAUNCHING LIVE TWILIO WHATSAPP SANDBOX SERVER
echo =================================================================
echo.

REM Activate Virtual Environment
call .venv\Scripts\activate.bat

REM Launch Twilio Webhook Server
python twilio_webhook_server.py

pause
