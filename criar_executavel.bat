@echo off
echo ========================================
echo  Criando executavel do BluePC
echo ========================================
echo.

echo Instalando PyInstaller...
python -m pip install pyinstaller

echo.
echo Criando executavel...
python -m PyInstaller --onefile --windowed --icon=icon.ico --name=BluePC system_info.py

echo.
echo ========================================
echo  Executavel criado com sucesso!
echo  Localizado em: dist\BluePC.exe
echo ========================================
echo.
pause
