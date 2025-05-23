from crewai import Agent, Task, Crew, Process
from config.llms import get_gpt35, get_gpt40
from crewai.tools import BaseTool
from config.settings import VERBOSE_MODE
from openai import OpenAI

# Classes para as ferramentas de pesquisa
class WebSearchTool(BaseTool):
    """
    Ferramenta para realizar pesquisas na web usando a OpenAI API.
    """
    name: str = "web_search"
    description: str = "Realiza pesquisas na web para encontrar informações atualizadas sobre um tópico específico."

    def _run(self, query: str) -> str:
        """
        Executa uma pesquisa na web usando a OpenAI API.
        Esta função utiliza a ferramenta de pesquisa da OpenAI para encontrar informações relevantes.

        Args:
            query: A consulta a ser pesquisada

        Returns:
            Resultados da pesquisa como texto
        """
        try:
            client = OpenAI()

            response = client.responses.create(
                model=get_gpt40(),
                tools=[{"type": "web_search"}],
                temperature=0.1,
                max_tokens=1024,
                input=query,
            )

            return response.output_text
        except Exception as e:
            return f"Erro ao fazer busca: {str(e)}"

# Função para obter o crew de pesquisa
def get_search_crew(user_input=None):
    """
    Cria e retorna um crew especializado em pesquisas web.
    Importante: criamos novas instâncias das ferramentas e do agente
    a cada chamada para evitar persistência indesejada de estado.
    """
    # Instanciar as ferramentas (criar novas instâncias a cada chamada)
    web_search_tool = WebSearchTool()

    # Criar um novo agente de pesquisa com as novas instâncias de ferramentas
    # Isso evita que o estado seja compartilhado entre diferentes consultas
    search_agent = Agent(
        role="Agente de Pesquisa Web",
        goal=f"Realizar pesquisas na web para encontrar informações atualizadas sobre: {user_input}",
        backstory="Você é um especialista em pesquisa e análise de dados da web. Sua função é encontrar as informações mais relevantes e confiáveis sobre qualquer tópico solicitado pelo usuário. Você sabe como avaliar fontes, extrair os dados mais importantes e apresentá-los de forma clara e organizada.",
        tools=[web_search_tool],
        allow_delegation=False,
        llm=get_gpt35(),
        verbose=VERBOSE_MODE
    )

    # Criar uma nova tarefa para a pesquisa atual
    search_task = Task(
        description=f"Pesquisar na web informações sobre: {user_input}. Utilize a ferramenta de pesquisa para encontrar informações relevantes e depois extraia o conteúdo dos sites mais promissores quando necessário para obter informações detalhadas.",
        expected_output="Um resumo completo e bem estruturado das informações encontradas, contendo fatos relevantes, números e detalhes importantes sobre o tópico pesquisado. Inclua as fontes utilizadas.",
        agent=search_agent
    )

    # Criar e retornar um novo crew com o agente e tarefa atualizados
    crew = Crew(
        agents=[search_agent],
        tasks=[search_task],
        process=Process.sequential,
        verbose=VERBOSE_MODE
    )

    return crew