@echo off
echo ========================================
echo  Instalando BluePC no Startup
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

set EXE_PATH=%~dp0dist\BluePC.exe

echo Copiando executavel para a pasta do programa...
if not exist "%PROGRAMFILES%\BluePC" mkdir "%PROGRAMFILES%\BluePC"
copy "%EXE_PATH%" "%PROGRAMFILES%\BluePC\BluePC.exe"

echo.
echo Removendo entradas antigas se existirem...
schtasks /Delete /TN "BluePC_Startup" /F >nul 2>&1
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "BluePC" /f >nul 2>&1
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\BluePC.lnk" >nul 2>&1

echo Criando tarefa agendada com PRIORIDADE ALTA...
schtasks /Create /TN "BluePC_Startup" /TR "\"%PROGRAMFILES%\BluePC\BluePC.exe\"" /SC ONLOGON /RL HIGHEST /DELAY 0000:05 /F

echo.
echo ========================================
echo  BluePC instalado com sucesso!
echo  
echo  Configuracoes aplicadas:
echo  - Tarefa agendada com prioridade ALTA
echo  - Inicio automatico no logon (5s delay)
echo  - Apenas UMA instancia sera iniciada
echo  
echo  O aplicativo sera um dos primeiros a
echo  iniciar quando voce ligar o computador.
echo ========================================
echo.
pause
