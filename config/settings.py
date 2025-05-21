import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env se existir
if os.path.exists('.env'):
    load_dotenv()

# Caminho para o arquivo de configuração do usuário
USER_CONFIG_DIR = os.path.expanduser('~/.assistente_config')
USER_CONFIG_FILE = os.path.join(USER_CONFIG_DIR, 'config.json')

# Garante que o diretório de configuração existe
os.makedirs(USER_CONFIG_DIR, exist_ok=True)

# Configurações padrão
DEFAULT_CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "assistant_name": os.getenv("ASSISTANT_NAME", "Assistente IA"),
    "temperature": float(os.getenv("TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("MAX_TOKENS", "1024")),
    "tema": "padrao",
    "email_sender": os.getenv("EMAIL_SENDER", ""),
    "email_password": os.getenv("EMAIL_PASSWORD", ""),
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587"))
}

# Carrega as configurações do usuário ou usa os valores padrão
def carregar_configuracoes():
    """Carrega as configurações do arquivo do usuário ou usa valores padrão."""
    if os.path.exists(USER_CONFIG_FILE):
        try:
            with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            # Mescla as configurações do usuário com os padrões para garantir que temos todas as chaves
            config = DEFAULT_CONFIG.copy()
            config.update(user_config)
            return config
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

# Salva as configurações do usuário
def salvar_configuracoes(config):
    """Salva as configurações do usuário."""
    try:
        with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

# Carrega as configurações
CONFIG = carregar_configuracoes()

# Define as variáveis globais para uso no resto do aplicativo
OPENAI_API_KEY = CONFIG.get("openai_api_key", "")
ASSISTANT_NAME = CONFIG.get("assistant_name", "Assistente IA")
TEMPERATURE = float(CONFIG.get("temperature", 0.7))
MAX_TOKENS = int(CONFIG.get("max_tokens", 1024))
TEMA_ATUAL = CONFIG.get("tema", "padrao")

# Atualiza as configurações durante a execução
def atualizar_configuracao(chave, valor):
    """Atualiza uma configuração específica e salva."""
    global OPENAI_API_KEY, ASSISTANT_NAME, TEMPERATURE, MAX_TOKENS, TEMA_ATUAL, CONFIG

    CONFIG[chave] = valor

    # Atualiza as variáveis globais
    if chave == "openai_api_key":
        OPENAI_API_KEY = valor
    elif chave == "assistant_name":
        ASSISTANT_NAME = valor
    elif chave == "temperature":
        TEMPERATURE = float(valor)
    elif chave == "max_tokens":
        MAX_TOKENS = int(valor)
    elif chave == "tema":
        TEMA_ATUAL = valor

    # Salva as alterações
    return salvar_configuracoes(CONFIG)
