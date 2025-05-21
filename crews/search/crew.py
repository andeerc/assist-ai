from crewai import Agent, Task, Crew, Process
from config.llms import get_gpt35, get_gpt40
from crewai.tools import BaseTool
from duckduckgo_search import DDGS
from typing import List, Dict, Any
import re
import requests
from bs4 import BeautifulSoup

# Ferramentas de pesquisa web
class WebSearchTool(BaseTool):
    """
    Ferramenta para realizar pesquisas na web usando DuckDuckGo.
    """
    name: str = "web_search"
    description: str = "Realiza pesquisas na web para encontrar informações atualizadas sobre um tópico específico."

    def _run(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Executa uma pesquisa na web.

        Args:
            query: A consulta a ser pesquisada
            max_results: Número máximo de resultados a retornar

        Returns:
            Uma lista de resultados contendo título, link e snippet
        """
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r["title"],
                        "link": r["href"],
                        "snippet": r["body"]
                    })
                return results
        except Exception as e:
            return [{"title": "Erro na pesquisa", "link": "", "snippet": f"Ocorreu um erro ao pesquisar: {str(e)}"}]

class WebExtractTool(BaseTool):
    """
    Ferramenta para extrair conteúdo de uma página web.
    """
    name: str = "web_extract"
    description: str = "Extrai o conteúdo principal de uma página web para análise detalhada."

    def _run(self, url: str) -> str:
        """
        Extrai o conteúdo de uma página web.

        Args:
            url: URL da página a ser extraída

        Returns:
            Conteúdo textual da página
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remover scripts, estilos e tags de formulário
            for script in soup(["script", "style", "form", "nav", "footer", "header"]):
                script.extract()

            # Obter texto
            text = soup.get_text(separator=' ')

            # Limpar espaços extras
            clean_text = re.sub(r'\s+', ' ', text).strip()

            # Limitar o tamanho do texto para evitar tokens muito grandes
            MAX_LENGTH = 8000
            if len(clean_text) > MAX_LENGTH:
                clean_text = clean_text[:MAX_LENGTH] + "... (conteúdo truncado)"

            return clean_text
        except Exception as e:
            return f"Erro ao extrair conteúdo da URL {url}: {str(e)}"

# Instanciando as ferramentas
web_search_tool = WebSearchTool()
web_extract_tool = WebExtractTool()

# Agente de pesquisa web
search_agent = Agent(
    role="Agente de Pesquisa Web",
    goal="Realizar pesquisas na web para encontrar informações atualizadas sobre o tópico solicitado pelo usuário: '{input}'",
    backstory="Você é um especialista em pesquisa e análise de dados da web. Sua função é encontrar as informações mais relevantes e confiáveis sobre qualquer tópico solicitado pelo usuário. Você sabe como avaliar fontes, extrair os dados mais importantes e apresentá-los de forma clara e organizada.",
    tools=[web_search_tool, web_extract_tool],
    allow_delegation=False,
    llm=get_gpt40(),
    verbose=True
)

# Tarefas de pesquisa
search_task = Task(
    description="Pesquisar na web informações sobre: '{input}'. Utilize a ferramenta de pesquisa para encontrar links relevantes e depois extraia o conteúdo dos sites mais promissores para obter informações detalhadas.",
    expected_output="Um resumo completo e bem estruturado das informações encontradas, contendo fatos relevantes, números e detalhes importantes sobre o tópico pesquisado. Inclua as fontes utilizadas.",
    agent=search_agent
)

# Função para obter o crew de pesquisa
def get_search_crew(user_input=None):
    """
    Cria e retorna um crew especializado em pesquisas web.
    """
    # Substituir {input} nos textos por user_input se fornecido
    if user_input:
        search_agent.goal = search_agent.goal.replace("{input}", user_input)
        search_task.description = search_task.description.replace("{input}", user_input)

    crew = Crew(
        agents=[search_agent],
        tasks=[search_task],
        process=Process.sequential,
        verbose=True
    )

    return crew