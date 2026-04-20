@echo off
echo ========================================
echo   Instalador - Informacoes do Sistema
echo ========================================
echo.

echo Instalando dependencias...
pip install -r "%~dp0requirements.txt"

echo.
echo Adicionando ao startup do Windows...
python "%~dp0system_info.py" --startup

echo.
echo ========================================
echo   Instalacao concluida!
echo   O programa ira iniciar com o Windows.
echo ========================================
echo.
pause
