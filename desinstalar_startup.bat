@echo off
echo ========================================
echo  Desinstalando BluePC do Startup
echo ========================================
echo.

REM Verifica se esta executando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Este script precisa ser executado como Administrador!
    echo Clique com botao direito e selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo Removendo tarefa agendada...
schtasks /Delete /TN "BluePC_Startup" /F >nul 2>&1

echo Removendo entrada do registro...
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "BluePC" /f >nul 2>&1

echo Removendo atalho do Startup (se existir)...
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\BluePC.lnk" >nul 2>&1

echo.
echo ========================================
echo  BluePC removido do startup!
echo  
echo  O aplicativo nao iniciara mais
echo  automaticamente com o Windows.
echo ========================================
echo.
pause
