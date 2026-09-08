@echo off
REM ===================================================================
REM  Abrir UI.bat  ->  Abre la interfaz grafica del clasificador.
REM  Doble clic para ejecutar. No muestra ventana de consola.
REM  (Los errores del modelo se muestran dentro de la propia ventana.)
REM ===================================================================
cd /d "%~dp0"
start "" "%~dp0alfonso\Scripts\pythonw.exe" "%~dp0app.py"
