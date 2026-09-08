@echo off
REM ===================================================================
REM  Abrir UI (consola).bat  ->  Igual que "Abrir UI" pero DEJANDO
REM  visible la consola, para ver mensajes/errores si algo falla.
REM  Util para depurar. La ventana no se cierra hasta pulsar una tecla.
REM ===================================================================
cd /d "%~dp0"
"%~dp0alfonso\Scripts\python.exe" "%~dp0app.py"
echo.
echo (La interfaz se cerro. Revisa arriba si hubo algun error.)
pause
