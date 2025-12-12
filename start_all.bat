@echo off
REM JointTrack - Complete Application Launcher (Windows)
REM Starts all services in separate windows

echo ============================================================
echo   JOINTTRACK - REAL-TIME AI COACHING
echo ============================================================
echo.
echo Starting all services...
echo.

REM Start Flask Backend
echo [1/3] Starting Flask Backend...
start "Flask Backend" cmd /k "python FlaskServer.py"
timeout /t 3 /nobreak > nul

REM Start AI Feedback Service
echo [2/3] Starting AI Feedback Service...
start "AI Feedback Service" cmd /k "python ai_feedback_service.py"
timeout /t 2 /nobreak > nul

REM Start React Frontend
echo [3/3] Starting React Frontend...
start "React Frontend" cmd /k "cd calisthenics-tracker && npm start"
timeout /t 2 /nobreak > nul

echo.
echo ============================================================
echo   ALL SERVICES STARTED
echo ============================================================
echo.
echo Services Running:
echo   - Flask Backend:        http://localhost:5000
echo   - AI Feedback Service:  Running in background
echo   - React Frontend:       http://localhost:3000
echo.
echo The React app should open in your browser automatically.
echo If not, open: http://localhost:3000
echo.
echo To stop all services, close all the command windows.
echo.
pause
