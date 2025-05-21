# Crews Manager
from typing import Dict, Any, Optional

# Importação dos crews
from crews.email.crew import get_email_crew
from crews.search.crew import get_search_crew

class CrewManager:
    """
    Gerencia todos os crews disponíveis no sistema.
    Responsável por selecionar e executar o crew apropriado com base no tipo de solicitação.
    """
    
    def __init__(self):
        self.available_crews = {
            "email": get_email_crew,
            "search": get_search_crew,
        }
    
    def get_crew(self, crew_type: str, user_input: str = None):
        """
        Obtém o crew apropriado com base no tipo.
        
        Args:
            crew_type: O tipo de crew a ser obtido (ex: "email")
            user_input: A entrada do usuário a ser processada pelo crew
            
        Returns:
            O crew solicitado, pronto para ser executado
        """
        if crew_type not in self.available_crews:
            raise ValueError(f"Crew do tipo '{crew_type}' não encontrado")
        
        return self.available_crews[crew_type](user_input)
    
    def execute_crew(self, crew_type: str, user_input: str) -> Dict[str, Any]:
        """
        Obtém e executa o crew apropriado com base no tipo.
        
        Args:
            crew_type: O tipo de crew a ser executado
            user_input: A entrada do usuário a ser processada pelo crew
            
        Returns:
            Resultado da execução do crew
        """
        crew = self.get_crew(crew_type, user_input)
        result = crew.kickoff()
        
        return {
            "crew_type": crew_type,
            "result": result,
        }
    def list_available_crews(self) -> Dict[str, str]:
        """
        Lista todos os crews disponíveis no sistema.
        
        Returns:
            Dicionário com os tipos de crews e suas descrições
        """
        descriptions = {
            "email": "Crew especializado na composição e envio de emails",
            "search": "Crew especializado em realizar pesquisas na web",
        }
        
        return {crew: descriptions.get(crew, "Sem descrição") for crew in self.available_crews.keys()}
