@echo off
cd /d "%~dp0"

echo ========================================
echo  Criando executavel do BluePC
echo ========================================
echo.

:: ── Localizar Python ──────────────────────────────────────────────────────────
set "PYTHON_EXE="

:: 1) Tentar py launcher (instalado em System32, funciona como admin)
where py >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_EXE=py"
    goto :found_python
)

:: 2) Tentar python no PATH normal
where python >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_EXE=python"
    goto :found_python
)

:: 3) Procurar nas pastas comuns do usuario atual
for %%U in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
) do (
    if exist %%U (
        set "PYTHON_EXE=%%~U"
        goto :found_python
    )
)

:: 4) Procurar no registro (instalacao do usuario)
for /f "usebackq tokens=2*" %%A in (
    `reg query "HKCU\Software\Python\PythonCore" /s /v ExecutablePath 2^>nul`
) do (
    if exist "%%B" (
        set "PYTHON_EXE=%%B"
        goto :found_python
    )
)

echo [ERRO] Python nao encontrado!
echo Instale o Python em https://www.python.org/downloads/
echo e marque a opcao "Add Python to PATH" durante a instalacao.
echo.
pause
exit /b 1

:found_python
echo Python encontrado: %PYTHON_EXE%
echo.

:: ── Instalar Dependencias ───────────────────────────────────────────────────────
echo Instalando dependencias do projeto...
"%PYTHON_EXE%" -m pip install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo Instalando PyInstaller...
"%PYTHON_EXE%" -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar PyInstaller.
    pause
    exit /b 1
)

:: ── Criar executavel ───────────────────────────────────────────────────────────
echo.
echo Criando executavel...
"%PYTHON_EXE%" -m PyInstaller --onefile --windowed --icon="%~dp0icon.ico" --name=BluePC --distpath="%~dp0dist" --workpath="%~dp0build" --specpath="%~dp0." "%~dp0system_info.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao criar o executavel. Verifique as mensagens acima.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Executavel criado com sucesso!
echo  Localizado em: dist\BluePC.exe
echo ========================================
echo.
pause
