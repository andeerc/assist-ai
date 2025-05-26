# Crews Manager
from typing import Dict, Any, Optional
import os
import importlib
import inspect # For checking class inheritance
from .base_crew import BaseCrew # Import BaseCrew

class CrewManager:
    """
    Gerencia todos os crews disponíveis no sistema.
    Responsável por selecionar e executar o crew apropriado com base no tipo de solicitação.
    Crews são descobertos dinamicamente a partir de subdiretórios na inicialização.
    """
    
    def __init__(self):
        """
        Inicializa o CrewManager. Chama o método _discover_crews
        para carregar dinamicamente todos os crews disponíveis.
        """
        self.available_crews: Dict[str, Dict[str, Any]] = {}
        self._discover_crews()
    
    def _discover_crews(self):
        """
        Descobre dinamicamente os crews disponíveis nos subdiretórios do pacote 'crews'.

        Itera sobre cada subdiretório em 'crews/'. Se um subdiretório (que não comece com '__')
        contiver um arquivo 'crew.py', ele tenta importar esse módulo.
        Dentro do módulo importado, procura por classes que são subclasses de
        `BaseCrew` (mas não `BaseCrew` em si).

        A primeira classe encontrada que satisfaz esses critérios é considerada
        o crew principal para aquele tipo (nome do subdiretório).
        O nome do subdiretório é usado como 'crew_type'.
        A descrição do crew é obtida do atributo de classe 'description' da classe do crew.

        Armazena os crews descobertos em `self.available_crews` com o formato:
        `{"crew_type": {"class": CrewClass, "description": "Crew description"}}`

        Erros durante a importação ou carregamento de um crew são impressos como avisos,
        permitindo que o restante dos crews seja carregado normalmente.
        """
        crews_dir = os.path.dirname(__file__) # Diretório atual (onde manager.py está, ex: /app/crews)
        
        for item in os.listdir(crews_dir):
            item_path = os.path.join(crews_dir, item)
            # Considera apenas diretórios que não começam com '__' (para ignorar __pycache__)
            # e que não são arquivos (como base_crew.py ou o próprio manager.py)
            if os.path.isdir(item_path) and not item.startswith('__'):
                # O nome do subdiretório torna-se o 'crew_type' (ex: "email", "search")
                crew_type = item 
                # Constrói o nome completo do módulo a ser importado (ex: "crews.email.crew")
                crew_module_name = f"crews.{crew_type}.crew" 
                
                try:
                    # Importa dinamicamente o módulo 'crew.py' do subdiretório
                    module = importlib.import_module(crew_module_name)
                    for attribute_name in dir(module):
                        attribute = getattr(module, attribute_name)
                        # Verifica se o atributo é uma classe, é uma subclasse de BaseCrew,
                        # e não é a própria classe BaseCrew.
                        if inspect.isclass(attribute) and \
                           issubclass(attribute, BaseCrew) and \
                           attribute is not BaseCrew:
                            # Armazena a classe e sua descrição.
                            # A descrição é usada pelo ChatManager para decidir qual crew usar.
                            description = getattr(attribute, "description", 
                                                  f"Crew {crew_type} (descrição não fornecida na classe).")
                            self.available_crews[crew_type] = {
                                "class": attribute, # A classe do crew em si
                                "description": description
                            }
                            # Assume que há apenas uma classe de crew principal por módulo 'crew.py'.
                            break 
                except ImportError as e:
                    # Captura erros se o módulo 'crew.py' não puder ser importado (ex: não existe, erro de sintaxe no módulo)
                    print(f"Aviso: Não foi possível importar o crew '{crew_type}' do módulo '{crew_module_name}': {e}")
                except Exception as e:
                    # Captura quaisquer outros erros durante o carregamento do crew (ex: erro na inicialização da classe do crew, se houver)
                    print(f"Aviso: Erro ao carregar o crew '{crew_type}' do módulo '{crew_module_name}': {e}")

    def get_crew(self, crew_type: str, user_input: Optional[str] = None) -> BaseCrew:
        """
        Obtém uma instância inicializada do crew solicitado.

        Args:
            crew_type (str): O tipo (nome) do crew a ser obtido. Corresponde ao nome do subdiretório.
            user_input (Optional[str]): A entrada do usuário (query/tarefa) a ser processada pelo crew.
                                         Este é passado para o construtor do crew.

        Returns:
            BaseCrew: Uma instância da classe do crew solicitado, pronta para ter seu método `kickoff()` chamado.

        Raises:
            ValueError: Se o `crew_type` solicitado não for encontrado entre os crews descobertos.
        """
        if crew_type not in self.available_crews:
            raise ValueError(f"Crew do tipo '{crew_type}' não encontrado. Crews disponíveis: {list(self.available_crews.keys())}")
        
        crew_data = self.available_crews[crew_type]
        crew_class = crew_data["class"] # Obtém a classe do crew do dicionário
        
        # Instancia a classe do crew, passando o user_input para seu __init__
        return crew_class(user_input=user_input)
    
    def execute_crew(self, crew_type: str, user_input: str) -> Dict[str, Any]:
        """
        Obtém uma instância de um crew e executa seu método `kickoff`.

        Este é o método principal para executar um crew. Ele primeiro obtém uma instância
        do crew especificado usando `get_crew` e, em seguida, chama `kickoff()` nessa instância.
        O `user_input` é obrigatório aqui, pois é essencial para a execução da tarefa do crew.

        Args:
            crew_type (str): O tipo do crew a ser executado.
            user_input (str): A entrada do usuário que o crew processará.

        Returns:
            Dict[str, Any]: Um dicionário contendo o resultado da execução do crew.
                            Espera-se que este dicionário inclua uma chave "result" com a saída principal,
                            mas pode ser estendido pela implementação `kickoff` do crew.
                            O `crew_type` também é adicionado/sobrescrito para rastreamento.
        """
        # get_crew retorna uma instância de uma subclasse de BaseCrew
        crew_instance = self.get_crew(crew_type, user_input) 
        
        # Chama o método kickoff na instância.
        # Cada crew (subclasse de BaseCrew) implementa seu próprio kickoff.
        execution_result = crew_instance.kickoff() 
        
        # Garante que o formato de retorno seja consistente, incluindo crew_type
        # e espalhando o dicionário retornado por kickoff().
        # Se execution_result já tiver "crew_type", ele será sobrescrito aqui,
        # garantindo que o crew_type correto seja retornado pelo manager.
        return {
            "crew_type": crew_type, 
            **execution_result 
        }

    def list_available_crews(self) -> Dict[str, str]:
        """
        Lista todos os crews disponíveis no sistema com suas respectivas descrições.

        As descrições são obtidas do atributo de classe `description` de cada
        classe de crew descoberta.

        Returns:
            Dict[str, str]: Um dicionário onde as chaves são os nomes (tipos) dos crews
                            e os valores são suas descrições.
        """
        return {
            crew_name: crew_data["description"]
            for crew_name, crew_data in self.available_crews.items()
        }

# --- Seção de Testes Conceituais ---
# Os testes reais devem ser implementados em um framework de testes como pytest ou unittest,
# preferencialmente em arquivos separados dentro de um diretório 'tests/'.

# Testes para CrewManager (`tests/test_crew_manager.py`):
# 1. Teste de Descoberta de Crews Válidos:
#    - Setup:
#      - Criar uma estrutura de diretórios mock em `tests/fixtures/crews/` com alguns subdiretórios:
#        - `tests/fixtures/crews/mock_crew_one/crew.py` (com uma classe válida `MockCrewOne(BaseCrew)` e com `description`)
#        - `tests/fixtures/crews/mock_crew_two/crew.py` (com uma classe válida `MockCrewTwo(BaseCrew)` e com `description`)
#      - Apontar o `CrewManager._discover_crews` para este diretório mock (pode requerer monkeypatching de `os.path.dirname` ou `os.listdir` ou passar o path).
#    - Ação: Instanciar `CrewManager`.
#    - Asserções:
#      - Verificar se `mock_crew_one` e `mock_crew_two` estão em `available_crews`.
#      - Verificar se as classes e descrições corretas foram carregadas para cada um.
#      - Verificar se `list_available_crews()` retorna as descrições esperadas.

# 2. Teste de Descoberta com Casos Inválidos:
#    - Setup (continuando com o diretório mock):
#      - `tests/fixtures/crews/mock_crew_no_desc/crew.py` (classe válida, mas sem atributo `description`)
#      - `tests/fixtures/crews/mock_crew_not_base/crew.py` (classe que não herda de BaseCrew)
#      - `tests/fixtures/crews/mock_crew_empty_dir/` (sem `crew.py`)
#      - `tests/fixtures/crews/mock_crew_import_error/crew.py` (com um erro de sintaxe/importação)
#      - `tests/fixtures/crews/_private_dir/crew.py` (diretório começando com '_', deve ser ignorado pelo `_discover_crews` se implementado para isso)
#      - `tests/fixtures/crews/not_a_dir.py` (um arquivo .py diretamente em `crews/`, deve ser ignorado)
#    - Ação: Instanciar `CrewManager` (apontando para `tests/fixtures/crews/`).
#    - Asserções:
#      - `mock_crew_no_desc` deve ser carregado, mas com uma descrição de fallback.
#      - `mock_crew_not_base`, `mock_crew_empty_dir`, `mock_crew_import_error`, `_private_dir`, `not_a_dir.py`
#        NÃO devem estar em `available_crews`.
#      - Verificar a saída de `print` para os avisos de erro de importação/carregamento (se possível capturar stdout).

# 3. Teste de Obtenção de Crew (`get_crew`):
#    - Setup: Usar um `CrewManager` instanciado com um `mock_crew_one` válido.
#    - Ação: Chamar `get_crew("mock_crew_one", user_input="test input")`.
#    - Asserções:
#      - Verificar se o objeto retornado é uma instância da classe `MockCrewOne`.
#      - Verificar se o atributo `user_input` da instância é "test input".
#    - Ação: Chamar `get_crew("crew_inexistente")`.
#    - Asserções: Verificar se `ValueError` é levantado com uma mensagem apropriada.

# 4. Teste de Execução de Crew (`execute_crew`):
#    - Setup:
#      - Definir uma classe `MockKickoffCrew(BaseCrew)` em `tests/fixtures/crews/mock_kickoff/crew.py`.
#      - No `kickoff` da `MockKickoffCrew`, ela deve retornar `{"result": f"Processed: {self.user_input}", "status": "success"}`.
#      - Instanciar `CrewManager` apontando para o diretório de fixtures.
#    - Ação: Chamar `manager.execute_crew("mock_kickoff", user_input="execute test")`.
#    - Asserções:
#      - Verificar se o resultado é `{"crew_type": "mock_kickoff", "result": "Processed: execute test", "status": "success"}`.
#    - Setup: Definir `MockErrorCrew(BaseCrew)` cujo `kickoff` levanta uma exceção específica.
#    - Ação: Chamar `execute_crew("mock_error_crew", user_input="trigger error")`.
#    - Asserções: Verificar como o erro é tratado (ex: se a exceção é propagada ou se o dicionário de resultado contém informações de erro).
#      Idealmente, o `kickoff` do crew deve tratar seus próprios erros e retornar um dict com status de erro.
