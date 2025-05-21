@echo off
echo ======================================================================
echo                        CONFIGURAÇÃO DO ASSIST AI
echo ======================================================================
echo.

:: Definir cores para melhor visibilidade
color 0B

:: Verificar se o Python está instalado
echo [*] Verificando instalação do Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERRO] Python não encontrado! Por favor, instale o Python 3.8 ou superior.
    echo        Visite https://www.python.org/downloads/ para fazer o download.
    pause
    exit /b 1
)
echo [OK] Python encontrado!
echo.

:: Verificar se o arquivo .env existe
echo [*] Verificando arquivo de configuração .env...
if not exist .env (
    echo [AVISO] Arquivo .env não encontrado. Criando modelo...
    echo # Configurações do ASSIST AI > .env
    echo # Preencha com suas credenciais >> .env
    echo. >> .env
    echo OPENAI_API_KEY=sua_chave_api_aqui >> .env
    echo EMAIL_SENDER=seu_email@gmail.com >> .env
    echo EMAIL_PASSWORD=sua_senha_ou_app_password >> .env
    echo SMTP_SERVER=smtp.gmail.com >> .env
    echo SMTP_PORT=587 >> .env
    echo. >> .env
    echo [OK] Arquivo .env criado. Você precisará editar este arquivo com suas credenciais.
) else (
    echo [OK] Arquivo .env encontrado!
)
echo.

:: Criar ambiente virtual se não existir
echo [*] Verificando ambiente virtual Python...
if not exist .venv (
    echo [*] Criando ambiente virtual...
    python -m venv .venv
    echo [OK] Ambiente virtual criado!
) else (
    echo [OK] Ambiente virtual encontrado!
)
echo.

:: Ativar o ambiente virtual
echo [*] Ativando ambiente virtual...
call .venv\Scripts\activate.bat
echo [OK] Ambiente virtual ativado!
echo.

:: Atualizar pip
echo [*] Atualizando pip para a versão mais recente...
python -m pip install --upgrade pip
echo [OK] Pip atualizado!
echo.

:: Instalar dependências
echo [*] Instalando dependências...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    color 0C
    echo [ERRO] Falha ao instalar dependências. Verifique sua conexão com a internet.
    pause
    exit /b 1
)
echo [OK] Dependências instaladas com sucesso!
echo.

:: Verificar chave da OpenAI
echo [*] Verificando configurações...
findstr /C:"OPENAI_API_KEY=sua_chave_api_aqui" .env >nul
if %errorlevel% equ 0 (
    color 0E
    echo [AVISO] A chave da API OpenAI não foi configurada no arquivo .env
    echo         Você precisará editar o arquivo .env antes de usar o aplicativo.
    echo.
)

:: Configuração concluída
color 0A
echo ======================================================================
echo                      CONFIGURAÇÃO CONCLUÍDA!
echo ======================================================================
echo.
echo Agora você pode executar o aplicativo usando o arquivo run.bat
echo.
echo Se precisar instalar atalhos no Menu Iniciar, execute:
echo   setup\install_menu.bat
echo.
pause