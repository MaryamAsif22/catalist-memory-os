@echo off
title Catalist Meeting Memory OS - Production Unified Application
cd /d "%~dp0"
cls
echo ======================================================================
echo           CATALIST MEDIA: UNIFIED MEETING INTELLIGENCE OS
echo ======================================================================
echo  Frontend: Maryam's Editorial Scandinavian Warm Ivory Interface
echo  Backend:  CataList Fixed Multi-Meeting Intelligence Engine
echo ======================================================================
echo.
echo [1/3] Detecting Python environment...

set "PYTHON_EXE=python"
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
)

echo [2/3] Starting Unified Server on http://localhost:8000...
echo [3/3] Opening browser window...
echo.

start "" "http://localhost:8000"
"%PYTHON_EXE%" app.py 8000 --no-open

pause
