@echo off
set "BAT_DIR=%~dp0"
echo %BAT_DIR%

cd %BAT_DIR%
cd ..\..




for /f "delims=" %%P in ('py -c "import sys; print(sys.executable)" 2^>nul') do (
    set "PYTHON_EXE=%%P"
)

if not defined PYTHON_EXE (
    for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do (
        set "PYTHON_EXE=%%P"
    )
)

if not defined PYTHON_EXE (
    echo No se ha podido obtener la ruta del ejecutable de Python.
    pause
    exit /b 1
)
set "PROGRAMApy=%BAT_DIR%instalar_herramientas.py"
echo Python encontrado en:
echo "%PYTHON_EXE%"


"%PYTHON_EXE%" "%PROGRAMApy%"
pause





