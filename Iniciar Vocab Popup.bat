@echo off
rem Inicia o Vocab Popup sem janela de console.
rem Funciona em qualquer PC: usa caminho relativo ao .bat e detecta o Python instalado.
setlocal

set "SCRIPT=%~dp0vocab_popup.py"

if not exist "%SCRIPT%" (
    echo [ERRO] Script nao encontrado: "%SCRIPT%"
    pause
    exit /b 1
)

rem 1) Py launcher sem console (mais confiavel, nao depende do PATH)
where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw "%SCRIPT%"
    exit /b 0
)

rem 2) pythonw no PATH
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%SCRIPT%"
    exit /b 0
)

rem 3) py launcher com console (fallback)
where py >nul 2>nul
if %errorlevel%==0 (
    start "" py "%SCRIPT%"
    exit /b 0
)

echo [ERRO] Python nao encontrado neste computador.
echo Instale o Python em https://python.org marcando a opcao "Add python.exe to PATH".
pause
exit /b 1
