@echo off
title Alfonso Vision - servidor (no cerrar mientras lo usas)
REM ===================================================================
REM  Abrir Alfonso Vision.bat  ->  Interfaz web "Alfonso Vision".
REM  Doble clic: arranca el servidor local y abre el navegador solo.
REM  DEJA esta ventana abierta mientras usas la app; cierrala para salir.
REM ===================================================================
cd /d "%~dp0"
"%~dp0alfonso\Scripts\python.exe" "%~dp0servidor.py"
pause
