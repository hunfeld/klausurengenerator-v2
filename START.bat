@echo off
REM ============================================================
REM Klausurengenerator v2.0 - Starter für Windows
REM ============================================================

echo.
echo ========================================
echo   KLAUSURENGENERATOR V2.0
echo ========================================
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    echo.
    echo Bitte installieren Sie Python 3.11 oder höher von:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python gefunden:
python --version
echo.

REM Prüfe ob PyQt6 installiert ist
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo PyQt6 ist nicht installiert. Installiere Abhängigkeiten...
    echo.
    pip install -r requirements.txt
    echo.
)

echo Starte Klausurengenerator...
echo.

REM Starte die Anwendung
python main.py

REM Falls Fehler auftritt
if errorlevel 1 (
    echo.
    echo ========================================
    echo   FEHLER beim Start!
    echo ========================================
    echo.
    pause
)
