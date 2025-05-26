import re
from crewai.tools import tool

def is_valid_email_address(email: str) -> bool:
    """Verifica se um endereço de email é válido usando expressão regular."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

@tool('validate_email_address_tool')
def validate_email_address_tool(email: str) -> bool:
    """
    Verifica se um endereço de email é válido usando expressão regular.
    Esta ferramenta pode ser usada por agentes para validar um endereço de email.
    """
    return is_valid_email_address(email)
