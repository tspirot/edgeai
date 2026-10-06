@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ==============================================================================
echo                К В О   Т Е   —   П И Р О Т С К И   А И   М О З А К
echo ==============================================================================
echo.
echo  Izaberite nacin pokretanja:
echo.
echo   [1] Veb interfejs (u pretrazivacu - preporuceno za Windows)
echo   [2] Prozor na ekranu (Pygame graficki mod)
echo   [3] Terminal CLI mod (tekstualni unos)
echo.
set /p izbor="Unesite broj (1, 2 ili 3) [Enter za 1]: "

if "%izbor%"=="2" goto pygame
if "%izbor%"=="3" goto cli

:web
echo.
echo Pokrecem Veb interfejs na http://localhost:8080...
python web_kvo_te.py
goto kraj

:pygame
echo.
echo Pokrecem Pygame graficki prozor...
python kvo_te.py --windowed
goto kraj

:cli
echo.
echo Pokrecem terminal CLI mod...
python kvo_te.py --cli
goto kraj

:kraj
if errorlevel 1 (
    echo.
    echo Doslo je do greske. Pritisnite bilo koji taster...
    pause
)
