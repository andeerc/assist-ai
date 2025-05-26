from crewai import Agent, Task, Crew, Process
from config.llms import get_llm # Import the new get_llm function
from config.settings import VERBOSE_MODE
from typing import Optional, Dict, Any
from ..base_crew import BaseCrew # Import BaseCrew
from crewai_tools import DuckDuckGoSearchRun # Import standard search tool

# --- SearchCrew Class ---
class SearchCrew(BaseCrew):
    """
    Crew especializado em realizar pesquisas na web usando DuckDuckGo.
    """
    description: str = "Realiza pesquisas na web para encontrar informações atualizadas sobre um tópico."

    def __init__(self, user_input: Optional[str] = None):
        super().__init__(user_input)
        self.search_agent = None
        self.search_task = None
        self.search_tool = DuckDuckGoSearchRun() # Initialize the tool

    def _setup_agents_and_tasks(self):
        """
        Configura os agentes e tarefas para o SearchCrew.
        """
        effective_user_input = self.user_input if self.user_input else "Pesquisa genérica na web. Por favor, especifique o tópico."

        self.search_agent = Agent(
            role="Agente de Pesquisa Web Especializado",
            goal=f"Realizar pesquisas detalhadas e eficazes na web para encontrar informações atualizadas sobre: '{effective_user_input}' utilizando a ferramenta DuckDuckGo.",
            backstory="Você é um especialista em pesquisa e análise de dados da web. Sua função é encontrar as informações mais relevantes, precisas e confiáveis sobre qualquer tópico solicitado pelo usuário. Você sabe como formular consultas de pesquisa eficazes, avaliar a credibilidade das fontes e extrair os dados mais importantes, apresentando-os de forma clara e organizada.",
            tools=[self.search_tool],
            allow_delegation=False, # Pode ser True se houver outros agentes para delegar tarefas de análise, por exemplo.
            llm=get_llm(model_name="gpt-3.5-turbo", temperature=0.1), # Use get_llm
            verbose=VERBOSE_MODE,
            # memory=True # Enable if context needs to be maintained by the agent
        )

        self.search_task = Task(
            description=f"Pesquisar exaustivamente na web informações sobre: '{effective_user_input}'. Utilize a ferramenta de pesquisa DuckDuckGo para encontrar as informações mais relevantes e atuais. Após a pesquisa inicial, analise os resultados e, se necessário, refine a busca ou explore links promissores para obter detalhes.",
            expected_output="Um resumo conciso e bem estruturado das informações encontradas, destacando fatos relevantes, dados importantes e, se possível, múltiplas perspectivas sobre o tópico pesquisado. Inclua as URLs das fontes primárias mais importantes.",
            agent=self.search_agent
        )

    def kickoff(self) -> Dict[str, Any]:
        """
        Inicia a execução do SearchCrew.
        """
        self._setup_agents_and_tasks()

        if not self.search_agent or not self.search_task:
            return {"status": "error", "message": "Agente de pesquisa ou tarefa não configurado."}

        search_processing_crew = Crew(
            agents=[self.search_agent],
            tasks=[self.search_task],
            process=Process.sequential,
            verbose=VERBOSE_MODE
        )

        result = search_processing_crew.kickoff()
        return {"result": result}

# A função get_search_crew(user_input) foi removida.
# O CrewManager agora irá instanciar SearchCrew(user_input) diretamente.