from crewai import Crew, Process

# Este arquivo foi mantido por compatibilidade com o código antigo
# As novas funcionalidades usam o gerenciador de crews em crews/manager.py
# e os crews específicos em suas respectivas pastas

def get_crew():
    """
    Função legada para obter crew.
    Para novas funcionalidades, use o CrewManager.
    """
    from crews.manager import CrewManager
    crew_manager = CrewManager()
    return crew_manager.get_crew("email")