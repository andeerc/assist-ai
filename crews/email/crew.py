from crewai import Agent, Task, Crew, Process
from config.llms import get_gpt35, get_gpt40
from crewai.tools import tool
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re
from config.settings import CONFIG
from typing import Optional

# Obtenha as credenciais do email das configurações ou variáveis de ambiente
EMAIL_SENDER = CONFIG.get("email_sender", os.getenv("EMAIL_SENDER", ""))
EMAIL_PASSWORD = CONFIG.get("email_password", os.getenv("EMAIL_PASSWORD", ""))
SMTP_SERVER = CONFIG.get("smtp_server", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
SMTP_PORT = int(CONFIG.get("smtp_port", os.getenv("SMTP_PORT", "587")))

# Funções para ferramentas
def is_valid_email(email: str) -> bool:
    """
    Verifica se um endereço de email é válido usando expressão regular.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

@tool('send_email')
def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Envia um email para o destinatário especificado com o assunto e corpo fornecidos.
    """
    try:
        # Criando mensagem MIME
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = f"Agents <agents@andersonc.dev.br>"
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

@tool('compose_email')
def compose_email(recipient: str, subject: str, body: str) -> str:
    """
    Compõe um email formatado com o assunto, corpo e destinatário fornecidos.
    """
    return f"""
Email composto com sucesso:
Para: {recipient}
Assunto: {subject}
Corpo:
{body}
"""

@tool
def validate_email(email: str) -> bool:
    """
    Verifica se um endereço de email é válido usando expressão regular.
    """
    return is_valid_email(email)

# Agente de email
email_agent = Agent(
    role="Agente de Email",
    goal="Compor e enviar emails profissionais baseados na solicitação do usuário: '{input}'",
    backstory="Você é um especialista em comunicação escrita, com vasta experiência em redação de emails formais e informais. Sua função é entender a solicitação do usuário e criar emails bem estruturados, claros e adequados ao contexto.",
    tools=[send_email, compose_email, validate_email],
    allow_delegation=False,
    llm=get_gpt40(),
    verbose=False
)

# Tarefas de email
compose_task = Task(
    description="Compor um email baseado na solicitação do usuário: '{input}'. Identifique o destinatário, o assunto e o corpo da mensagem a partir da solicitação.",
    expected_output="Um email bem estruturado, com destinatário, assunto e corpo claros e adequados ao contexto da solicitação.",
    agent=email_agent
)

send_task = Task(
    description="Enviar o email composto para o destinatário especificado.",
    expected_output="Confirmação de que o email foi enviado com sucesso.",
    agent=email_agent
)

# Função para obter o crew de email
def get_email_crew(user_input=None):
    """
    Cria e retorna um crew especializado em emails.
    """
    # Substituir {input} nos textos por user_input se fornecido
    if user_input:
        email_agent.goal = email_agent.goal.replace("{input}", user_input)
        compose_task.description = compose_task.description.replace("{input}", user_input)

    crew = Crew(
        agents=[email_agent],
        tasks=[compose_task, send_task],
        process=Process.sequential,
        verbose=False
    )

    return crew