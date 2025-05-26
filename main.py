#!/usr/bin/env python3
import os
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.status import Status
from rich.layout import Layout
from rich.align import Align
from rich import box
import shutil
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory, FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style as PTStyle
from prompt_toolkit.key_binding import KeyBindings

# Importa as configurações do arquivo settings.py
from config.settings import (
    ASSISTANT_NAME, TEMA_ATUAL, atualizar_configuracao, CONFIG, salvar_configuracoes
)

# Importar o chat completion e gerenciador de crews
from chat_completion import ChatManager
from crews.manager import CrewManager

# Inicializando o console do Rich e o aplicativo Typer
console = Console()
app = typer.Typer()

# Inicializa o gerenciador de chat e de crews globalmente
# para manter o estado da conversa entre as entradas.
chat_manager = ChatManager()
crew_manager = CrewManager()

# Obtém as dimensões do terminal
terminal_width, terminal_height = shutil.get_terminal_size()

# Comandos do menu
COMANDOS = {
    "/ajuda": "Exibe informações de ajuda",
    "/config": "Abre o menu de configurações",
    "/env": "Informações sobre configurações sensíveis (.env)",
    "/limpar": "Limpa a tela do terminal",
    "/tema": "Muda o tema visual (padrão, escuro, claro, natureza)",
    "/verbose": "Ativa/desativa o modo verbose",
    "/reset": "Reinicia o histórico da conversa",
    "/sair": "Encerra o aplicativo"
}

# Temas disponíveis
TEMAS = {
    "padrao": {"principal": "cyan", "secundaria": "green", "destaque": "yellow", "erro": "red"},
    "escuro": {"principal": "blue", "secundaria": "purple", "destaque": "yellow", "erro": "red"},
    "claro": {"principal": "magenta", "secundaria": "blue", "destaque": "yellow", "erro": "red"},
    "natureza": {"principal": "green", "secundaria": "blue", "destaque": "yellow", "erro": "red"},
}

# Tema atual (pode ser alterado pelo usuário)
tema_atual = TEMA_ATUAL

# Configura história, autocompletar e histórico persistente
try:
    # Tenta usar histórico de arquivo persistente
    history_file = os.path.expanduser('~/.assistente_history')
    history = FileHistory(history_file)
except:
    # Se falhar, usa histórico em memória
    history = InMemoryHistory()
completer = WordCompleter(COMANDOS, ignore_case=True)

def get_tema():
    """Retorna as cores do tema atual."""
    return TEMAS[tema_atual]

def limpar_tela():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Função para exibir os comandos básicos na lateral direita
def exibir_comandos_lateral():
    # Cria um layout dividido em duas colunas
    layout = Layout()
    layout.split_column(
        Layout(name="principal"),
        Layout(name="prompt", size=3)
    )

    # Divide a área principal em conteúdo principal e área lateral
    layout["principal"].split_row(
        Layout(name="conteudo", ratio=3),
        Layout(name="lateral", ratio=1, minimum_size=20)
    )

    # Cria o painel de comandos para a área lateral
    comandos_panel = Panel(
        "\n".join([f"[bold]{cmd}[/] - {desc}" for cmd, desc in COMANDOS.items()]),
        title="[bold yellow]Comandos Básicos[/]",
        border_style="yellow",
        padding=(1, 2)
    )

    layout["lateral"].update(Align.center(comandos_panel))

    return layout["lateral"]

# Essa versão antiga de exibir_menu_principal não é mais necessária, pois já foi substituída acima

def exibir_ajuda():
    """Exibe informações de ajuda sobre o assistente com formatação aprimorada."""
    cores = get_tema()
    limpar_tela()

    console.print(Panel(
        "[bold]Sobre o Aplicativo[/bold]\n\n"
        "Este aplicativo usa as bibliotecas Rich e Typer para criar uma interface de linha de comando interativa.\n"
        "Ele possui diferentes funcionalidades que podem ser acessadas através dos comandos disponíveis.\n"
        "Você pode usar os comandos especiais listados abaixo ou interagir usando texto em linguagem natural.",
        border_style=cores['principal'],
        title="Ajuda do Aplicativo",
        expand=False,
        box=box.ROUNDED
    ))
    console.print()

    # Exibe tabela de comandos
    tabela = Table(show_header=True, header_style=f"bold {cores['principal']}", box=box.ROUNDED, border_style=cores['principal'])
    tabela.add_column("Comando", style=cores['principal'])
    tabela.add_column("Descrição")

    for cmd, desc in COMANDOS.items():
        tabela.add_row(cmd, desc)

    console.print(Panel(tabela, title="Comandos Disponíveis", border_style=cores['principal'], box=box.ROUNDED))
    console.print()

    # Dicas de uso
    dicas = Table.grid(padding=1)
    dicas.add_column()
    dicas.add_row(f"• Use [{cores['principal']}]/config[/{cores['principal']}] para configurar suas preferências")
    dicas.add_row(f"• Use [{cores['principal']}]/tema[/{cores['principal']}] seguido do nome do tema para personalizar a aparência")
    dicas.add_row(f"• Use as setas ↑↓ para navegar pelo histórico de comandos")
    dicas.add_row(f"• Use TAB para autocompletar comandos")
    dicas.add_row(f"• Use Ctrl+L para limpar a tela")

    console.print(Panel(dicas, title="Dicas", border_style=cores['principal'], box=box.ROUNDED))
    console.print()

def exibir_info_env():
    """Exibe informações sobre configurações sensíveis no arquivo .env."""
    cores = get_tema()
    limpar_tela()

    console.print(Panel(
        "[bold]Configurações Sensíveis[/bold]\n\n"
        "Para configurar chaves de API e outras informações sensíveis, você deve editar o arquivo .env na raiz do projeto.\n\n"
        "Estas configurações são sensíveis e não devem ser armazenadas no aplicativo por motivos de segurança.\n\n"
        f"[{cores['principal']}]Configurações disponíveis no arquivo .env:[/{cores['principal']}]\n"
        "OPENAI_API_KEY=sua_chave_api_openai\n"
        "EMAIL_SENDER=seu_email@gmail.com\n"
        "EMAIL_PASSWORD=sua_senha_ou_senha_de_app\n"
        "SMTP_SERVER=smtp.gmail.com\n"
        "SMTP_PORT=587\n\n"
        f"[{cores['secundaria']}]Nota:[/{cores['secundaria']}] Essas configurações são lidas automaticamente pelo aplicativo durante a inicialização.",
        border_style=cores['principal'],
        title="Arquivo de Configurações .env",
        expand=False,
        box=box.ROUNDED
    ))

    # Aguarda o usuário pressionar Enter para voltar
    console.print()
    Prompt.ask("[bold]Pressione Enter para voltar[/bold]")
    return

def configurar_app():
    """Exibe o menu de configurações para que o usuário possa ajustar as configurações."""
    global tema_atual
    cores = get_tema()
    limpar_tela()

    console.print(Panel(
        "[bold]Menu de Configurações[/bold]\n\n"
        "Configure seu assistente para personalizá-lo conforme suas preferências.\n\n"
        "[italic]Nota: As configurações sensíveis como chaves API e credenciais de email devem ser configuradas no arquivo .env[/italic]",
        border_style=cores['principal'],
        title="Configurações do Assistente",
        expand=False,
        box=box.ROUNDED
    ))
    console.print()# Exibe as configurações atuais
    table = Table(title="Configurações Atuais", box=box.ROUNDED, border_style=cores['principal'])
    table.add_column("Configuração", style=cores['principal'])
    table.add_column("Valor Atual")
    table.add_row("1. Nome do Assistente", ASSISTANT_NAME)
    table.add_row("2. Tema", tema_atual)
    table.add_row("3. Voltar", "Retorna ao assistente sem salvar")
    table.add_row("4. Salvar e Voltar", "Salva as configurações e retorna")
    console.print(table)
    console.print()

    # Obtém a escolha do usuário
    choice = Prompt.ask(
        "Escolha uma opção",
        choices=["1", "2", "3", "4"],
        default="4"
    )    # Configura com base na escolha
    if choice == "1":
        # Nome do assistente
        novo_nome = Prompt.ask(
            "[bold]Digite o novo nome para o assistente[/bold]",
            default=ASSISTANT_NAME
        )
        atualizar_configuracao("assistant_name", novo_nome)
        console.print(f"[{cores['secundaria']}]Nome do assistente atualizado para: {novo_nome}[/{cores['secundaria']}]")

    elif choice == "2":
        # Tema
        console.print(f"[{cores['secundaria']}]Temas disponíveis:[/{cores['secundaria']}]")
        for i, tema in enumerate(TEMAS.keys(), 1):
            console.print(f"{i}. {tema}")

        opcao_tema = Prompt.ask(
            "[bold]Escolha um tema (1-4)[/bold]",
            choices=["1", "2", "3", "4"],
            default="1"  # padrao
        )
        tema_escolhido = list(TEMAS.keys())[int(opcao_tema) - 1]
        atualizar_configuracao("tema", tema_escolhido)
        tema_atual = tema_escolhido
        console.print(f"[{get_tema()['principal']}]Tema atualizado para: {tema_escolhido}[/{get_tema()['principal']}]")

    elif choice == "3":
        # Volta sem salvar
        return

    elif choice == "4":
        # Salva e volta
        salvar_configuracoes(CONFIG)
        console.print(f"[{cores['secundaria']}]Configurações salvas com sucesso![/{cores['secundaria']}]")
        return

    # Recursivamente mostra o menu até o usuário escolher voltar
    return configurar_app()

def configurar_email():
    """Exibe as instruções para configurar email usando o arquivo .env."""
    cores = get_tema()
    limpar_tela()

    console.print(Panel(
        "[bold]Configurações de Email[/bold]\n\n"
        "Para configurar seu serviço de email, você precisa editar o arquivo .env na raiz do projeto.\n\n"
        "Estas configurações são sensíveis e não devem ser armazenadas no aplicativo por motivos de segurança.\n\n"
        f"[{cores['principal']}]Edite as seguintes variáveis no arquivo .env:[/{cores['principal']}]\n"
        "EMAIL_SENDER=seu_email@gmail.com\n"
        "EMAIL_PASSWORD=sua_senha_ou_senha_de_app\n"
        "SMTP_SERVER=smtp.gmail.com\n"
        "SMTP_PORT=587\n\n"
        f"[{cores['secundaria']}]Nota:[/{cores['secundaria']}] Se você usar o Gmail, é recomendável criar uma senha de aplicativo específica.",
        border_style=cores['principal'],
        title="Configurações de Email",
        expand=False,
        box=box.ROUNDED
    ))

    # Aguarda o usuário pressionar Enter para voltar
    console.print()
    Prompt.ask("[bold]Pressione Enter para voltar ao menu de configurações[/bold]")
    return

def processar_entrada(entrada):
    # Se a entrada estiver vazia, simplesmente retorna sem fazer nada
    # Isso evita que o programa pule para a próxima linha quando o usuário apenas aperta Enter
    if not entrada.strip():
        return True

    entrada_lower = entrada.lower().strip()

    if entrada_lower == "/sair":
        return False
    elif entrada_lower == "/ajuda":
        exibir_ajuda()
    elif entrada_lower == "/config":
        configurar_app()
    elif entrada_lower == "/env":
        exibir_info_env()
    elif entrada_lower == "/limpar":
        limpar_tela()
    elif entrada_lower == "/reset":
        chat_manager.reset_conversation()
        console.print(f"[{get_tema()['principal']}]Histórico da conversa reiniciado.[/{get_tema()['principal']}]")
    elif entrada_lower == "/verbose":
        # Alternar o modo verbose
        from config.settings import VERBOSE_MODE
        novo_valor = not VERBOSE_MODE
        atualizar_configuracao("verbose_mode", novo_valor)
        status = "ativado" if novo_valor else "desativado"
        console.print(f"[{get_tema()['principal']}]Modo verbose {status}[/{get_tema()['principal']}]")
    elif entrada_lower.startswith("/tema"):
        partes = entrada_lower.split(maxsplit=1)
        if len(partes) > 1 and partes[1] in TEMAS:
            global tema_atual
            tema_atual = partes[1]
            atualizar_configuracao("tema", tema_atual)
            salvar_configuracoes(CONFIG)
            console.print(f"[{get_tema()['principal']}]Tema alterado para: {tema_atual}[/{get_tema()['principal']}]")
        else:            # Se o usuário não especificar um tema válido, mostrar os temas disponíveis
            console.print(f"[{get_tema()['destaque']}]Temas disponíveis:[/{get_tema()['destaque']}]")
            for i, tema in enumerate(TEMAS.keys(), 1):
                console.print(f"[{get_tema()['secundaria']}]{i}. {tema}[/{get_tema()['secundaria']}]")

            console.print(f"[{get_tema()['erro']}]Use /tema seguido do nome do tema. Exemplo: /tema claro[/{get_tema()['erro']}]")
    else:
        cores = get_tema()
        result_to_print = f"[bold {cores['erro']}]Não foi possível processar sua solicitação.[/bold {cores['erro']}]"

        # Verifica se o modo verbose está ativado
        from config.settings import VERBOSE_MODE        # Se verbose estiver ativo, executar sem mostrar o loader
        if VERBOSE_MODE:
            # Utiliza as instâncias globais de chat_manager e crew_manager
            # A linha chat_manager.reset_conversation() foi removida daqui
            # As instanciações de chat_manager e crew_manager foram removidas daqui
            result = chat_manager.handle_user_input(entrada)

            # Define as cores para a resposta
            # Verifica o tipo de ação a ser tomada
            if result['action'] == 'direct_response':
                result_to_print = result['response']
            elif result['action'] == 'use_crew':
                # Utiliza um crew específico
                try:
                    crew_result = crew_manager.execute_crew(result['crew_type'], entrada)
                    result_to_print = crew_result['result']
                except ValueError as e:
                    result_to_print = f"[bold {cores['erro']}]Erro:[/bold {cores['erro']}] {str(e)}"
        else:
            # Com o modo verbose desativado, mostra o loader
            with Status("", spinner="dots"):
                # Utiliza as instâncias globais de chat_manager e crew_manager
                # A linha chat_manager.reset_conversation() foi removida daqui
                # As instanciações de chat_manager e crew_manager foram removidas daqui
                result = chat_manager.handle_user_input(entrada)

                # Define as cores para a resposta
                # Verifica o tipo de ação a ser tomada
                if result['action'] == 'direct_response':
                    result_to_print = result['response']
                elif result['action'] == 'use_crew':
                    # Utiliza um crew específico
                    try:
                        crew_result = crew_manager.execute_crew(result['crew_type'], entrada)
                        result_to_print = crew_result['result']
                    except ValueError as e:
                        result_to_print = f"[bold {cores['erro']}]Erro:[/bold {cores['erro']}] {str(e)}"

        console.print(Panel(
            f"[italic]{result_to_print}[/]",
            border_style=cores['secundaria'],
            box=box.ROUNDED
        ))

    return True

# Função para exibir o menu principal com comandos no estilo do código de exemplo
def exibir_menu_principal():
    cores = get_tema()
    limpar_tela()

    # Tabela de comandos
    table = Table(show_header=True, header_style=f"bold {cores['principal']}", box=box.ROUNDED, border_style=cores['principal'])
    table.add_column("Comando", style=cores['principal'])
    table.add_column("Descrição")

    # Adiciona os comandos à tabela
    for cmd, desc in COMANDOS.items():
        table.add_row(cmd, desc)

    # Exibe o painel com os comandos
    console.print(Panel(
        table,
        title="Comandos Disponíveis",
        border_style=cores['principal'],
        expand=False,
        box=box.ROUNDED
    ))
    console.print()

    # Mensagem de boas-vindas/instrução
    console.print(Panel(
        f"[{cores['destaque']}]Digite um comando ou texto para interagir com o aplicativo.[/{cores['destaque']}]",
        border_style=cores['secundaria'],
        box=box.ROUNDED
    ))
    console.print()

# Função para prompt estilizado com comandos à direita
def prompt_com_comandos():
    # Configura o estilo do prompt
    estilo = criar_estilo_prompt()

    # Texto para o prompt (manteremos este fixo)
    prompt_texto = "> "

    # Utilizando um contexto específico para o prompt atual
    from prompt_toolkit.application import get_app

    # Esta função é chamada sempre que precisamos do rprompt
    def get_rprompt():
        app = get_app()
        # Se não há texto digitado, mostra a ajuda completa
        if not app.current_buffer.text:
            return "Tab: completar | ↑↓: histórico | Ctrl+L: limpar"
        else:
            return "↑↓: histórico"


    # Lista de comandos para autocompletar
    completer = WordCompleter(list(COMANDOS.keys()), ignore_case=True)

    # Configura sessão do prompt com histórico persistente e autocompletar
    session = PromptSession(
        history=history,
        auto_suggest=AutoSuggestFromHistory(),
        completer=completer,
        style=estilo,
        key_bindings=bindings_personalizados(),
        enable_history_search=True  # Habilita explicitamente a busca no histórico
    )

    # Exibe o prompt com texto de ajuda à direita que muda (mas não desaparece) quando o usuário digita
    return session.prompt(prompt_texto, rprompt=get_rprompt())

def criar_estilo_prompt():
    """Cria um estilo personalizado para o prompt."""
    cores = get_tema()
    cor_principal = cores["principal"]

    # Converte os nomes de cores do rich para formato aceito pelo prompt_toolkit
    if cor_principal == "cyan":
        prompt_color = "turquoise"
    elif cor_principal == "blue":
        prompt_color = "blue"
    elif cor_principal == "magenta":
        prompt_color = "magenta"
    elif cor_principal == "green":
        prompt_color = "green"
    else:
        prompt_color = "ansicyan"

    return PTStyle.from_dict({
        # Estilos para o prompt
        'prompt': f'bold {prompt_color}',
        # Estilos para o texto digitado
        '': 'white',
        # Estilo para autocompletar
        'completion-menu.completion': f'bg:{prompt_color} white',
        'completion-menu.completion.current': f'bg:ansibrightyellow ansiblack',
        'scrollbar.background': 'bg:#88aaaa',
        'scrollbar.button': 'bg:#222222',
    })

def bindings_personalizados():
    """Cria bindings de teclas personalizados."""
    bindings = KeyBindings()

    @bindings.add('c-l')  # Ctrl+L
    def limpar_tela_binding(event):
        limpar_tela()

    # Garantindo que as setas funcionem para navegação no histórico
    @bindings.add('up')
    def previous_history(event):
        # Apenas encaminha o evento para o handler padrão
        event.current_buffer.history_backward()

    @bindings.add('down')
    def next_history(event):
        # Apenas encaminha o evento para o handler padrão
        event.current_buffer.history_forward()

    return bindings

def exibir_boas_vindas():
    """Exibe uma mensagem de boas-vindas para o usuário com estilo aprimorado."""
    cores = get_tema()
    limpar_tela()

    console.print(Panel(
        f"[bold {cores['principal']}]{ASSISTANT_NAME}[/bold {cores['principal']}]\n\n"
        f"[{cores['secundaria']}]Interface de linha de comando avançada com Typer e Rich[/{cores['secundaria']}]",
        border_style=cores['principal'],
        title="Bem-vindo",
        expand=False,
        box=box.ROUNDED
    ))
    console.print()

    # Mensagem de instrução
    console.print(Panel(
        f"[{cores['destaque']}]Estou pronto para ajudar! Digite em linguagem natural o que deseja.[/{cores['destaque']}]\n"
        f"[{cores['secundaria']}]Use os comandos especiais para acessar funcionalidades específicas.[/{cores['secundaria']}]",
        border_style=cores['secundaria'],
        box=box.ROUNDED
    ))
    console.print()

def main():
    limpar_tela()

    # Exibe tela de boas-vindas estilizada
    exibir_boas_vindas()
    # Exibe menu principal com tabela de comandos
    exibir_menu_principal()

    continuar = True
    while continuar:
        # Captura a entrada do usuário com o prompt estilizado
        entrada = prompt_com_comandos()

        # Se o usuário apenas apertou Enter sem digitar nada,
        # continue no loop sem fazer nada
        if not entrada.strip():
            continue

        # Processa a entrada do usuário
        continuar = processar_entrada(entrada)

    # Mensagem de despedida com cores do tema atual
    cores = get_tema()
    console.print(Panel(
        f"[bold {cores['principal']}]Obrigado por usar o aplicativo! Até logo![/bold {cores['principal']}]",
        border_style=cores['principal'],
        box=box.ROUNDED
    ))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Programa interrompido pelo usuário. Até logo![/]")
    except Exception as e:
        console.print(f"[bold red]Erro inesperado: {e}[/]")