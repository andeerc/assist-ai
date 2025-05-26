from crewai import Agent, Task, Crew, Process
from config.llms import get_llm # Import the new get_llm function
from crewai.tools import tool
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re
from config.settings import CONFIG, VERBOSE_MODE
from typing import Optional, Dict, Any
from ..base_crew import BaseCrew
from tools.email_tools import validate_email_address_tool # Import the moved tool

# Obtenha as credenciais do email das configurações ou variáveis de ambiente
EMAIL_SENDER = CONFIG.get("email_sender", os.getenv("EMAIL_SENDER", ""))
EMAIL_PASSWORD = CONFIG.get("email_password", os.getenv("EMAIL_PASSWORD", ""))
SMTP_SERVER = CONFIG.get("smtp_server", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
SMTP_PORT = int(CONFIG.get("smtp_port", os.getenv("SMTP_PORT", "587")))

# Helper function - not a tool itself, used by send_email_tool and compose_email_tool
def is_valid_email_address(email: str) -> bool:
    """Verifica se um endereço de email é válido usando expressão regular."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Tools for the Email Agent
@tool('send_email_tool')
def send_email_tool(recipient: str, subject: str, body: str) -> str:
    """
    Envia um email para o destinatário especificado com o assunto e corpo fornecidos.
    """
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return "Erro: Credenciais de email (remetente ou senha) não configuradas. Verifique o arquivo .env ou as configurações."
    if not is_valid_email_address(recipient): # Use renamed validator
        return f"Erro: Endereço de email do destinatário inválido: {recipient}"
    try:
        # Criando mensagem MIME
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = f"Assistente Virtual IA <{EMAIL_SENDER}>" # Use configured sender
        msg['To'] = recipient

        # Anexando o corpo do texto
        texto = MIMEText(body, 'plain', 'utf-8')
        msg.attach(texto)

        # Configuração do servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)        # Envio do email
        server.send_message(msg)
        server.quit()

        return f"Email enviado com sucesso para {recipient}."
    except Exception as e:
        return f"Falha ao enviar email: {str(e)}"

@tool('compose_email_tool') # Renamed tool
def compose_email_tool(recipient: str, subject: str, body: str) -> str:
    """
    Compõe um email formatado com o assunto, corpo e destinatário fornecidos.
    """
    if not is_valid_email_address(recipient):
        return f"Erro: Endereço de email do destinatário inválido ao compor: {recipient}"
    return f"""
Email composto com sucesso:
Para: {recipient}
Assunto: {subject}
Corpo:
{body}
"""

# The validate_email_address_tool is now imported from tools.email_tools.py
# The local definition has been removed.

# --- EmailCrew Class ---
class EmailCrew(BaseCrew):
    """
    Crew especializado na composição e envio de emails.
    Utiliza agentes para identificar detalhes da solicitação do usuário,
    compor o email e enviá-lo.
    """
    description: str = "Compõe e envia emails com base nas solicitações do usuário."

    def __init__(self, user_input: Optional[str] = None):
        super().__init__(user_input)
        self.email_agent = None
        self.compose_task = None

    def _setup_agents_and_tasks(self):
        """
        Configura os agentes e tarefas para o EmailCrew.
        Este método é chamado internamente pelo kickoff.
        """
        effective_user_input = self.user_input if self.user_input else "Tarefa genérica de email, por favor, esclareça a solicitação."

        self.email_agent = Agent(
            role="Agente de Email Especializado",
            goal=f"Analisar a solicitação do usuário para identificar destinatário, assunto e corpo do email. Em seguida, compor o email e, se a intenção de envio for clara, enviá-lo usando as ferramentas disponíveis. Solicitação do usuário: '{effective_user_input}'",
            backstory="Você é um especialista em comunicação escrita, treinado para redigir emails formais e informais. Sua função é entender as necessidades do usuário, criar emails bem estruturados e realizar o envio quando apropriado, validando informações como o email do destinatário.",
            tools=[send_email_tool, compose_email_tool, validate_email_address_tool],
            allow_delegation=False,
            llm=get_llm(model_name="gpt-4o", temperature=0.1), # Use get_llm
            verbose=VERBOSE_MODE,
            # memory=True # CrewAI's memory can be enabled if needed
        )

        self.compose_task = Task(
            description=f"Com base na solicitação do usuário: '{effective_user_input}', identifique todos os componentes necessários (destinatário, assunto, corpo). Componha o email. Se a solicitação indicar claramente que o email deve ser enviado (ex: 'envie um email para...', 'mande agora para...'), utilize a ferramenta de envio. Caso contrário, apenas componha o email para revisão.",
            expected_output="Um email bem estruturado e formatado, com destinatário, assunto e corpo claramente definidos. Se o envio foi solicitado e realizado, a saída deve incluir a confirmação do envio. Se apenas composto, a saída deve ser o email composto.",
            agent=self.email_agent
        )

    def kickoff(self) -> Dict[str, Any]:
        """
        Inicia a execução do EmailCrew.
        Cria os agentes e tarefas necessários e executa o crew.
        """
        self._setup_agents_and_tasks()

        if not self.email_agent or not self.compose_task:
            # This case should ideally not be reached if user_input is always provided
            # or handled gracefully in _setup_agents_and_tasks.
            return {"status": "error", "message": "Agentes ou tarefas não foram configurados corretamente devido à falta de input ou outro erro."}

        # Create the Crew for this specific kickoff
        email_processing_crew = Crew(
            agents=[self.email_agent],
            tasks=[self.compose_task],
            process=Process.sequential,
            verbose=VERBOSE_MODE
        )

        result = email_processing_crew.kickoff()
        # The result from crew.kickoff() is usually the output of the last task.
        # We wrap it in a dictionary as expected by CrewManager.
        return {"result": result}

# A função get_email_crew(user_input) foi removida.
# O CrewManager agora irá instanciar EmailCrew(user_input) diretamente.