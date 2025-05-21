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