@echo off
echo ========================================
echo TESTE DE DETECCAO DE GPU
echo ========================================
echo.

echo 1. Nomes das GPUs detectadas:
echo --------------------------------------------------
wmic path win32_VideoController get Name
echo.

echo 2. VRAM das GPUs:
echo --------------------------------------------------
wmic path win32_VideoController get AdapterRAM
echo.

echo 3. Informacoes completas:
echo --------------------------------------------------
wmic path win32_VideoController get Name,AdapterRAM,PNPDeviceID
echo.

echo ========================================
echo Copie e cole toda essa saida para analise
echo ========================================
pause
