@echo off
echo Desinstalando Assist AI do menu Iniciar...

:: Define o diretório de destino no menu Iniciar
set STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Assist AI

:: Verifica se o diretório existe
if exist "%STARTMENU_DIR%" (
    :: Remove os atalhos
    if exist "%STARTMENU_DIR%\Assist AI.lnk" del "%STARTMENU_DIR%\Assist AI.lnk"
    if exist "%STARTMENU_DIR%\Configurar Assist AI.lnk" del "%STARTMENU_DIR%\Configurar Assist AI.lnk"

    :: Remove o diretório
    rmdir "%STARTMENU_DIR%"

    echo.
    echo Desinstalação concluída! Os atalhos foram removidos do menu Iniciar.
) else (
    echo.
    echo Os atalhos não foram encontrados no menu Iniciar.
)

:: Pergunta ao usuário se deseja também remover os arquivos do programa
echo.
choice /C SN /M "Deseja também remover completamente o programa do computador? (S/N)"
if errorlevel 2 goto :fim
if errorlevel 1 goto :remover_programa

:remover_programa
echo.
echo ATENÇÃO: Esta ação irá excluir todos os arquivos do programa!
echo.
choice /C SN /M "Tem certeza que deseja continuar? (S/N)"
if errorlevel 2 goto :fim

echo.
echo Removendo arquivos do programa...
cd ..
rmdir /S /Q "%~dp0"
echo Programa removido com sucesso!
goto :eof

:fim
echo.
echo Desinstalação do menu Iniciar concluída.
pause