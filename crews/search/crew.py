from crewai import Agent, Task, Crew, Process
from config.llms import get_gpt35, get_gpt40
from crewai.tools import BaseTool
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
import re
import random
import time
from typing import List, Dict, Any, Optional
from config.settings import VERBOSE_MODE

# Lista de user agents para evitar bloqueios
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
]

# Classes para as ferramentas de pesquisa
class WebSearchTool(BaseTool):
    """
    Ferramenta para realizar pesquisas na web usando o browser interno.
    """
    name: str = "web_search"
    description: str = "Realiza pesquisas na web para encontrar informações atualizadas sobre um tópico específico."

    def _run(self, query: str, max_results: int = 5) -> str:
        """
        Executa uma pesquisa na web usando um browser interno.

        Args:
            query: A consulta a ser pesquisada
            max_results: Número máximo de resultados a retornar

        Returns:
            Resultados da pesquisa como texto
        """
        try:
            # Codificar a consulta para URL
            encoded_query = quote_plus(query)

            # Construir URLs de busca alternativas para aumentar a chance de sucesso
            search_urls = [
                f"https://www.bing.com/search?q={encoded_query}&count={max_results}",
                f"https://html.duckduckgo.com/html/?q={encoded_query}",
                f"https://search.brave.com/search?q={encoded_query}&count={max_results}"
            ]

            search_results = []

            # Tentar cada URL até que uma funcione
            for search_url in search_urls:
                if VERBOSE_MODE:
                    print(f"Tentando busca em: {search_url}")

                try:
                    # Adicionar um pequeno delay para evitar bloqueios
                    time.sleep(random.uniform(0.5, 2.0))

                    # Rotacionar o user agent
                    headers = {
                        'User-Agent': random.choice(USER_AGENTS),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': 'https://www.google.com/',
                        'DNT': '1',  # Do Not Track
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'cross-site',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0'
                    }

                    # Realizar a requisição
                    response = requests.get(search_url, headers=headers, timeout=15)
                    response.raise_for_status()

                    # Parsear o HTML
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Extrair os resultados com base no motor de busca
                    if "bing.com" in search_url:
                        results = self._extract_bing_results(soup, max_results)
                    elif "duckduckgo.com" in search_url:
                        results = self._extract_duckduckgo_results(soup, max_results)
                    elif "brave.com" in search_url:
                        results = self._extract_brave_results(soup, max_results)
                    else:
                        results = []

                    # Adicionar resultados encontrados
                    search_results.extend(results)

                    # Se encontramos resultados suficientes, pare de tentar outros motores de busca
                    if len(search_results) >= max_results:
                        search_results = search_results[:max_results]
                        break

                except Exception as e:
                    if VERBOSE_MODE:
                        print(f"Erro na busca com {search_url}: {str(e)}")
                    # Se falhar com um motor de busca, tente o próximo
                    continue

            # Formatar os resultados
            if not search_results:
                # Tentar uma abordagem mais simples como último recurso
                search_results = self._fallback_search(query, max_results)

            if not search_results:
                return "Não foi possível encontrar resultados para esta consulta. Tente reformular sua pesquisa."

            formatted_text = f"Resultados da busca para: '{query}'\n\n"

            for i, result in enumerate(search_results, 1):
                formatted_text += f"{i}. {result.get('title', 'Sem título')}\n"
                formatted_text += f"   URL: {result.get('link', 'Sem link')}\n"
                formatted_text += f"   {result.get('snippet', 'Sem descrição')}\n\n"

            return formatted_text

        except Exception as e:
            return f"Ocorreu um erro ao pesquisar: {str(e)}"

    def _extract_bing_results(self, soup, max_results):
        """Extrai resultados da pesquisa Bing"""
        results = []
        # Tenta vários seletores possíveis para maior robustez
        selectors = ['li.b_algo', '.b_algo', '.b_caption', '.b_snippetItems']

        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items[:max_results]:
                    try:
                        # Tenta encontrar o título, link e snippet de várias maneiras
                        title_element = item.select_one('h2') or item.select_one('.b_title') or item.select_one('a')
                        link_element = item.select_one('h2 a') or item.select_one('.b_title a') or item.select_one('a')
                        snippet_element = item.select_one('p') or item.select_one('.b_snippet') or item.select_one('.b_snippetBigText')

                        if title_element and link_element:
                            title = title_element.get_text(strip=True)
                            link = link_element.get('href', '')
                            snippet = snippet_element.get_text(strip=True) if snippet_element else "Sem descrição"

                            # Verifica se o link é válido
                            if link and link.startswith('http'):
                                results.append({
                                    'title': title,
                                    'link': link,
                                    'snippet': snippet
                                })
                    except Exception:
                        continue

                # Se encontrou resultados com este seletor, não precisa tentar os outros
                if results:
                    break

        return results

    def _extract_duckduckgo_results(self, soup, max_results):
        """Extrai resultados da pesquisa DuckDuckGo"""
        results = []
        # Tenta vários seletores possíveis
        selectors = ['.result', '.web-result', '.results_links', '.links_main']

        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items[:max_results]:
                    try:
                        # Tenta extrair os elementos de diferentes maneiras
                        title_element = (item.select_one('.result__title') or
                                        item.select_one('.result__a') or
                                        item.select_one('a.result__a'))

                        link_element = (item.select_one('.result__url') or
                                       item.select_one('a.result__a') or
                                       item.select_one('a[href]'))

                        snippet_element = (item.select_one('.result__snippet') or
                                          item.select_one('.result__snippet') or
                                          item.select_one('.result__description'))

                        if title_element:
                            title = title_element.get_text(strip=True)
                            link = ""

                            # Tenta obter o link de diferentes maneiras
                            if link_element:
                                if link_element.has_attr('href'):
                                    link = link_element['href']
                                else:
                                    link = link_element.get_text(strip=True)

                            # Se o link for relativo ou texto, tenta normalizá-lo
                            if link and not (link.startswith('http://') or link.startswith('https://')):
                                if '.' in link:
                                    link = 'https://' + link

                            snippet = ""
                            if snippet_element:
                                snippet = snippet_element.get_text(strip=True)

                            # Adiciona apenas se tiver pelo menos título e link válido
                            if title and link and link.startswith(('http://', 'https://')):
                                results.append({
                                    'title': title,
                                    'link': link,
                                    'snippet': snippet
                                })
                    except Exception:
                        continue

                # Se encontrou resultados com este seletor, não precisa tentar os outros
                if results:
                    break

        return results

    def _extract_brave_results(self, soup, max_results):
        """Extrai resultados da pesquisa Brave"""
        results = []
        # Tenta vários seletores possíveis
        selectors = ['.snippet', '.result', '.fdb', '.snippet-container', '.card']

        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items[:max_results]:
                    try:
                        # Tenta diferentes combinações de seletores
                        title_element = (item.select_one('.snippet-title') or
                                        item.select_one('.title') or
                                        item.select_one('h3') or
                                        item.select_one('a'))

                        link_element = (item.select_one('.snippet-url') or
                                       item.select_one('.url') or
                                       item.select_one('a') or
                                       item.select_one('cite'))

                        snippet_element = (item.select_one('.snippet-description') or
                                          item.select_one('.description') or
                                          item.select_one('p'))

                        if title_element:
                            # Extrair o título
                            title = title_element.get_text(strip=True)

                            # Extrair o link
                            link = ""
                            if link_element:
                                if link_element.name == 'a' and link_element.has_attr('href'):
                                    link = link_element['href']
                                else:
                                    link = link_element.get_text(strip=True)

                            # Corrigir link se necessário
                            if link and not (link.startswith('http://') or link.startswith('https://')):
                                if '.' in link:
                                    link = 'https://' + link

                            # Extrair o snippet
                            snippet = ""
                            if snippet_element:
                                snippet = snippet_element.get_text(strip=True)

                            # Adicionar se tiver pelo menos título e link
                            if title and link:
                                results.append({
                                    'title': title,
                                    'link': link,
                                    'snippet': snippet or "Sem descrição disponível"
                                })
                    except Exception:
                        continue

                # Se encontrou resultados com este seletor, não precisa tentar os outros
                if results:
                    break

        return results

    def _fallback_search(self, query, max_results):
        """Busca simplificada usando a abordagem mais básica possível como último recurso"""
        results = []
        try:
            # Usar Bing que tende a ser mais permissivo
            encoded_query = quote_plus(query)
            url = f"https://www.bing.com/search?q={encoded_query}"

            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            }

            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Pegar todos os links da página
            links = soup.find_all('a')
            for link in links:
                href = link.get('href', '')
                # Filtrar apenas links externos relevantes
                if href.startswith(('http://', 'https://')) and 'bing' not in href and 'microsoft' not in href:
                    title = link.get_text(strip=True)
                    if title and len(title) > 5:  # Ignorar links muito curtos
                        results.append({
                            'title': title,
                            'link': href,
                            'snippet': "Informação extraída da web"
                        })

                        if len(results) >= max_results:
                            break
        except Exception as e:
            if VERBOSE_MODE:
                print(f"Erro na busca fallback: {str(e)}")

        return results

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
            # Usar um user agent aleatório
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                'Referer': 'https://www.google.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            # Pequeno delay para evitar bloqueios
            time.sleep(random.uniform(0.5, 2.0))

            # Fazer a requisição
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            # Parsear o HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remover elementos que geralmente não contêm conteúdo útil
            for element in soup(['script', 'style', 'head', 'header', 'footer',
                                'nav', 'aside', 'noscript', 'iframe', 'form']):
                element.decompose()

            # Verifica o domínio para extração específica
            domain = urlparse(url).netloc

            # Extração específica para sites populares
            if 'news.google.com' in domain:
                content = self._extract_google_news(soup)
            elif 'g1.globo.com' in domain or 'globo.com' in domain:
                content = self._extract_globo(soup)
            elif 'uol.com.br' in domain:
                content = self._extract_uol(soup)
            elif 'folha.uol.com.br' in domain:
                content = self._extract_folha(soup)
            elif 'estadao.com.br' in domain:
                content = self._extract_estadao(soup)
            else:
                # Tentativa de extração genérica
                content = self._extract_generic_content(soup)

            # Se a extração específica falhar, cai para a genérica
            if not content or len(content) < 100:
                content = self._extract_generic_content(soup)

            # Limitar o tamanho do texto para evitar tokens muito grandes
            MAX_LENGTH = 8000
            if len(content) > MAX_LENGTH:
                content = content[:MAX_LENGTH] + "... (conteúdo truncado)"

            return content
        except Exception as e:
            return f"Erro ao extrair conteúdo da URL {url}: {str(e)}"

    def _extract_google_news(self, soup):
        """Extração específica para Google News"""
        content_elements = soup.select('.xrnccd')
        if content_elements:
            return '\n\n'.join([elem.get_text(separator=' ', strip=True) for elem in content_elements])
        return ""

    def _extract_globo(self, soup):
        """Extração específica para sites da Globo"""
        content_elements = soup.select('.content-text__container') or soup.select('.mc-article-body')
        if content_elements:
            return '\n\n'.join([elem.get_text(separator=' ', strip=True) for elem in content_elements])
        return ""

    def _extract_uol(self, soup):
        """Extração específica para UOL"""
        content_elements = soup.select('.text') or soup.select('.content-text')
        if content_elements:
            return '\n\n'.join([elem.get_text(separator=' ', strip=True) for elem in content_elements])
        return ""

    def _extract_folha(self, soup):
        """Extração específica para Folha de S. Paulo"""
        content_elements = soup.select('.c-news__body') or soup.select('.news-text')
        if content_elements:
            return '\n\n'.join([elem.get_text(separator=' ', strip=True) for elem in content_elements])
        return ""

    def _extract_estadao(self, soup):
        """Extração específica para Estadão"""
        content_elements = soup.select('.n--noticia__content') or soup.select('.news-content')
        if content_elements:
            return '\n\n'.join([elem.get_text(separator=' ', strip=True) for elem in content_elements])
        return ""

    def _extract_generic_content(self, soup):
        """Extração genérica para outros sites"""
        # Busca por elementos comuns que geralmente contêm o conteúdo principal
        content_selectors = [
            'article', '.article', '.post', '.content', '.entry-content',
            '#content', '#main', 'main', '.main-content', '.body', '.text',
            '.story', '.story-body', '.news-article', '.post-content'
        ]

        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                return '\n\n'.join([elem.get_text(separator=' ', strip=True) for elem in elements])

        # Se não encontrou com seletores específicos, tenta pegar o texto do body
        # removendo cabeçalhos e rodapés
        body = soup.body
        if body:
            # Obter texto
            text = body.get_text(separator=' ')
            # Limpar espaços extras
            clean_text = re.sub(r'\s+', ' ', text).strip()
            return clean_text

        # Última opção: pegar todo o texto visível
        return soup.get_text(separator=' ')

# Função para obter o crew de pesquisa
def get_search_crew(user_input=None):
    """
    Cria e retorna um crew especializado em pesquisas web.
    Importante: criamos novas instâncias das ferramentas e do agente
    a cada chamada para evitar persistência indesejada de estado.
    """
    # Instanciar as ferramentas (criar novas instâncias a cada chamada)
    web_search_tool = WebSearchTool()
    web_extract_tool = WebExtractTool()

    # Criar um novo agente de pesquisa com as novas instâncias de ferramentas
    # Isso evita que o estado seja compartilhado entre diferentes consultas
    search_agent = Agent(
        role="Agente de Pesquisa Web",
        goal=f"Realizar pesquisas na web para encontrar informações atualizadas sobre: {user_input}",
        backstory="Você é um especialista em pesquisa e análise de dados da web. Sua função é encontrar as informações mais relevantes e confiáveis sobre qualquer tópico solicitado pelo usuário. Você sabe como avaliar fontes, extrair os dados mais importantes e apresentá-los de forma clara e organizada.",
        tools=[web_search_tool, web_extract_tool],
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