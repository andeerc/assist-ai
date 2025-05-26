# Assist AI

<div align="center">
<img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+"/>
<img src="https://img.shields.io/badge/GPT--4o-Powered-brightgreen.svg" alt="GPT-4o Powered"/>
<img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"/>
<img src="https://img.shields.io/badge/CrewAI-Framework-orange.svg" alt="CrewAI Framework"/>
<img src="https://img.shields.io/badge/Multi--Agent-System-blueviolet.svg" alt="Multi-Agent System"/>
<img src="https://img.shields.io/badge/Windows-Compatible-00a2ed.svg" alt="Windows Compatible"/>
</div>

<div align="center">
<p><strong>Um assistente de IA avançado com múltiplos agentes especializados trabalhando em equipe</strong></p>
<p><em>Envie emails, realize pesquisas na web e obtenha respostas inteligentes - tudo a partir de uma interface de terminal elegante</em></p>
</div>

<p align="center">
  <img src="https://raw.githubusercontent.com/andersponders/assist-ai/main/assets/assist-ai-demo.gif" alt="Assist AI Interface" width="80%"/>
</p>

## 🌟 Destaques

- **🧠 Inteligência Adaptativa**: Sistema de chat completion que identifica automaticamente quando acionar agentes especializados
- **👥 Arquitetura Multi-Agente**: Utiliza o framework CrewAI para coordenar equipes de agentes especializados
- **📧 Email Integrado**: Compose e envie emails diretamente do terminal
- **🔍 Pesquisa Web**: Encontre informações atualizadas na internet sem sair do aplicativo
- **🎨 Interface Personalizável**: Múltiplos temas visuais para uma experiência agradável
- **🧩 Design Modular**: Arquitetura extensível para adicionar facilmente novos agentes e funcionalidades

## Funcionalidades

- **Sistema de Chat Completion**: Processa entradas do usuário e decide quando usar resposta direta ou acionar um crew especializado
- **Crews Especializados**:
  - **Email**: Compõe e envia emails
  - **Pesquisa Web**: Realiza buscas e extrai informações da web
- **Interface de Terminal**: Interface amigável com Rich e Typer
- **Personalizável**: Temas visuais configuráveis
- **Expansível**: Arquitetura modular para adicionar novos crews e funcionalidades

## Requisitos

- Python 3.8 ou superior
- Conexão com a Internet
- Chave de API da OpenAI
- Credenciais de email (para o crew de email)

## Instalação

### Método 1: Configuração Manual

1. Clone este repositório ou faça o download dos arquivos
2. Execute `setup.bat` para configurar o ambiente virtual e instalar dependências
3. Edite o arquivo `.env` na raiz do projeto e adicione suas credenciais:
   ```
   OPENAI_API_KEY=sua_chave_api_openai
   EMAIL_SENDER=seu_email@gmail.com
   EMAIL_PASSWORD=sua_senha_ou_senha_de_app
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```
4. Execute `run.bat` para iniciar o aplicativo

### Método 2: Instalação no Menu Iniciar

1. Siga os passos 1-3 acima
2. Execute `install_menu.bat` para criar atalhos no Menu Iniciar
3. Acesse o programa através do Menu Iniciar do Windows

### Desinstalação

1. **Remoção dos Atalhos do Menu Iniciar**: Execute `uninstall_menu.bat` para remover os atalhos do Menu Iniciar
2. **Desinstalação Completa**: O script `uninstall_menu.bat` também oferece a opção de remover completamente o programa do computador

## Uso

### Comandos Disponíveis

- `/ajuda`: Exibe informações de ajuda
- `/config`: Abre o menu de configurações
- `/env`: Informações sobre configurações sensíveis (.env)
- `/limpar`: Limpa a tela do terminal
- `/tema`: Muda o tema visual (padrão, escuro, claro, natureza)
- `/reset`: Reinicia o histórico da conversa atual.
- `/sair`: Encerra o aplicativo

### Exemplos de Uso

- **Conversa Normal**: "Qual a previsão do tempo para amanhã?"
- **Envio de Email**: "Envie um email para contato@exemplo.com com o título 'Reunião'"
- **Pesquisa Web**: "Pesquise sobre as novidades em inteligência artificial"

## Estrutura do Projeto

```
assist-ai/
├── agents/
│   ├── conversation.py
│   ├── email.py
│   └── manager.py
├── config/
│   ├── crew.py
│   ├── llms.py
│   └── settings.py
├── crews/
│   ├── email/
│   │   └── crew.py
│   └── search/
│       └── crew.py
├── tools/
├── chat_completion.py
├── main.py
├── requirements.txt
├── run.bat
├── setup.bat
└── install_menu.bat
```

## Desempenho

O aplicativo usa o GPT-4o para processamento de linguagem natural e decisões inteligentes, proporcionando respostas precisas e contextuais.

## 🔧 Estendendo o Assistente

A arquitetura modular do Assist AI facilita a adição de novas funcionalidades através de Crews e Ferramentas.

### Adicionando um Novo Crew

Crews são equipes de agentes especializados que realizam tarefas específicas. Para adicionar um novo crew:

1.  **Crie o Diretório do Crew:**
    Crie um novo subdiretório em `crews/`. O nome do diretório se tornará o `crew_type` (identificador do seu crew). Por exemplo: `crews/my_new_crew/`.

2.  **Crie o Arquivo `crew.py`:**
    Dentro do novo diretório (ex: `crews/my_new_crew/`), crie um arquivo chamado `crew.py`.

3.  **Defina a Classe do Crew:**
    No seu `crew.py`, defina uma classe que herda de `crews.base_crew.BaseCrew`. Esta classe irá encapsular a lógica do seu novo crew.

    ```python
    from typing import Optional, Dict, Any
    from crewai import Agent, Task, Process
    from config.llms import get_llm # Para obter instâncias de LLM configuradas
    from ..base_crew import BaseCrew
    # Importe quaisquer ferramentas que seu crew possa precisar
    # from tools.my_custom_tool import MyCustomTool 

    class MyNewCrew(BaseCrew):
        description: str = "Descrição concisa do que este novo crew faz."

        def __init__(self, user_input: Optional[str] = None):
            super().__init__(user_input)
            self.llm = get_llm(model_name="gpt-3.5-turbo", temperature=0.2) # Ou outro modelo
            # Inicialize agentes e tarefas como None ou configure-os aqui se não dependerem de user_input
            self.my_agent = None
            self.my_task = None

        def _setup_agents_and_tasks(self):
            """Configura os agentes e tarefas para este crew."""
            if not self.user_input:
                # Lide com user_input ausente se necessário
                effective_input = "tarefa padrão"
            else:
                effective_input = self.user_input
            
            self.my_agent = Agent(
                role="Especialista em Minha Nova Tarefa",
                goal=f"Executar minha nova tarefa baseada em: {effective_input}",
                backstory="Sou um agente expert em realizar minha nova tarefa eficientemente.",
                tools=[], # Adicione instâncias de ferramentas aqui: [MyCustomTool()]
                llm=self.llm,
                verbose=True # Ou use VERBOSE_MODE das configurações
            )

            self.my_task = Task(
                description=f"Realizar a operação X com base na entrada: {effective_input}",
                expected_output="O resultado esperado da operação X.",
                agent=self.my_agent
            )

        def kickoff(self) -> Dict[str, Any]:
            """Inicia a execução do crew."""
            self._setup_agents_and_tasks()
            
            if not self.my_agent or not self.my_task:
                return {"status": "error", "message": "Agente ou tarefa não configurado."}

            crew = Process(
                agents=[self.my_agent],
                tasks=[self.my_task],
                process=Process.sequential,
                verbose=True # Ou use VERBOSE_MODE
            )
            result = crew.kickoff()
            return {"result": result} # Adapte conforme a saída do seu crew
    ```

4.  **Atributo `description`:**
    Na sua classe de crew (ex: `MyNewCrew`), defina um atributo de classe `description` (string). Esta descrição é usada pelo `CrewManager` para listar crews e pelo `ChatManager` (LLM) para decidir quando delegar uma tarefa ao seu crew. Ex: `description: str = "Realiza a tarefa X e Y."`

5.  **Descoberta Automática:**
    O `CrewManager` (em `crews/manager.py`) descobre e carrega automaticamente qualquer classe que herde de `BaseCrew` de arquivos `crew.py` localizados em subdiretórios diretos de `crews/`.

6.  **Atualize o `ChatManager`:**
    Para que o assistente principal saiba quando usar seu novo crew, você precisará atualizar o *system prompt* no método `ChatManager.get_completion` em `chat_completion.py`. Adicione seu `crew_type` (o nome do subdiretório) à lista de opções e forneça exemplos claros de quando o usuário pode querer usar este crew.

    Exemplo de modificação no system prompt:
    ```
    ...
    2.  **Encaminhar para um crew especializado (`use_crew`):**
        -   **Crew de Email (`email`):** ...
        -   **Crew de Pesquisa (`search`):** ...
        -   **Crew de Minha Nova Tarefa (`my_new_crew`):** Use para solicitações como 'Faça X com Y', 'Preciso que você execute minha nova tarefa sobre Z.'
            -   *Exceção:* Se o usuário perguntar 'O que é o crew de minha nova tarefa?', responda diretamente.
    ...
    **Formato da Resposta (JSON OBRIGATÓRIO):**
    ...
        "crew_type": null (SE action for "direct_response") OU "email" OU "search" OU "my_new_crew" (SE action for "use_crew"),
    ...
    ```

### Adicionando uma Nova Ferramenta (Tool)

Ferramentas são usadas por agentes dentro dos crews para interagir com o mundo exterior ou realizar operações específicas.

1.  **Crie o Arquivo da Ferramenta:**
    Crie um novo arquivo Python no diretório `tools/` (ex: `tools/my_new_tool.py`).

2.  **Defina a Classe da Ferramenta:**
    No seu arquivo, defina uma classe que herda de `crewai_tools.BaseTool`.

    ```python
    from crewai_tools import BaseTool

    class MyCustomTool(BaseTool):
        name: str = "Nome Descritivo da Minha Ferramenta"
        description: str = "Descrição clara do que esta ferramenta faz e como usá-la. Inclua os parâmetros esperados."

        def _run(self, argument_1: str, argument_2: Optional[int] = None) -> str:
            # A lógica da sua ferramenta vai aqui
            # Exemplo:
            # if argument_2:
            #     return f"Ferramenta executada com {argument_1} e {argument_2}."
            # return f"Ferramenta executada com {argument_1}."
            pass # Implemente sua lógica
    ```
    -   **`name`**: Um nome curto e descritivo para a ferramenta.
    -   **`description`**: Uma descrição detalhada do que a ferramenta faz, para que o LLM do agente saiba como e quando usá-la. Seja específico sobre os argumentos que a ferramenta espera.
    -   **`_run`**: O método que executa a lógica da ferramenta. Os argumentos deste método devem corresponder aos que o LLM do agente passará.

3.  **Use a Ferramenta em um Agente:**
    Importe e instancie sua nova ferramenta na definição de um agente dentro de um arquivo `crew.py` de um crew:

    ```python
    # Em crews/nome_do_seu_crew/crew.py
    from crewai import Agent
    from tools.my_new_tool import MyCustomTool # Importe sua ferramenta

    # ... dentro da configuração do seu agente ...
    meu_agente = Agent(
        role="Agente que Usa Minha Ferramenta",
        goal="Usar MyCustomTool para alcançar um objetivo.",
        backstory="Sou um agente projetado para usar MyCustomTool.",
        tools=[MyCustomTool()], # Adicione uma instância da sua ferramenta aqui
        # ... outras configurações do agente ...
    )
    ```

O agente agora terá acesso à sua ferramenta personalizada e poderá decidir usá-la com base em sua descrição e no objetivo da tarefa.