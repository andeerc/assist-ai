@echo off
echo ======================================================================
echo                       INICIANDO ASSIST AI
echo ======================================================================
echo.

:: Definir cores para melhor visibilidade
color 0B

:: Verificar se o ambiente virtual existe
if not exist .venv (
    color 0C
    echo [ERRO] Ambiente virtual não encontrado!
    echo        Execute setup.bat primeiro para configurar o ambiente.
    pause
    exit /b 1
)

:: Verificar se o arquivo .env existe
if not exist .env (
    color 0E
    echo [AVISO] Arquivo .env não encontrado! 
    echo         Algumas funcionalidades podem não funcionar corretamente.
    echo         Recomendamos executar setup.bat primeiro.
    echo.
    choice /C SN /M "Deseja continuar mesmo assim (S/N)?"
    if errorlevel 2 exit /b 0
    echo.
)

:: Verificar se o arquivo main.py existe
if not exist main.py (
    color 0C
    echo [ERRO] Arquivo main.py não encontrado!
    echo        Verifique a instalação do aplicativo.
    pause
    exit /b 1
)

:: Ativar o ambiente virtual
echo [*] Ativando ambiente virtual...
call .venv\Scripts\activate.bat

:: Iniciar o aplicativo
echo [*] Iniciando o aplicativo...
echo.

:: Limpar a tela antes de iniciar
timeout /t 1 > nul
cls

:: Iniciar o aplicativo
python main.py

:: Desativar o ambiente virtual ao sair
call .venv\Scripts\deactivate.bat

:: Mostrar mensagem final após a execução
color 07
echo.
echo Aplicativo encerrado.
echo.
pause