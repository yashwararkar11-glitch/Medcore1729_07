@echo off
title Streamlit App
cd /d "%~dp0"

rem ---- Change this if your script has a different name ----
set APP=app.py

if not exist "%APP%" (
  echo Could not find %APP% in %cd%
  echo Edit run_app.bat and set APP to your script's name.
  pause
  exit /b 1
)

rem Use a local virtual environment if one exists
if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"

rem Open the browser after a short delay, then start the server (works offline)
start "" cmd /c "timeout /t 4 >nul & start http://localhost:8501"
python -m streamlit run "%APP%" --server.port 8501 --server.headless true --browser.gatherUsageStats false

pause
