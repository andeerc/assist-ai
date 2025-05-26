#!/usr/bin/env python3
# OpenAI import will be handled by get_openai_client
from config.llms import get_openai_client # Import the new client getter
from typing import Dict, List, Optional
import json
# OPENAI_API_KEY is not directly needed here anymore as client handles it.

class ChatManager:
    """
    Gerencia a interação com o usuário usando o modelo de chat completion da OpenAI.
    Determina quando acionar um crew específico com base na entrada do usuário.

    Integração com a Memória de Agents do CrewAI:
    - Persistência de Estado: No design atual (conforme visto em `crews/email/crew.py` e `crews/search/crew.py`),
      os agentes e tarefas do CrewAI são recriados a cada nova solicitação do usuário.
      Isso significa que eles não mantêm um estado ou memória interna persistente entre diferentes
      chamadas de `crew.kickoff()`. A frase "Importante: criamos novas instâncias do agente e tarefas
      a cada chamada para evitar persistência indesejada de estado." em `crews/email/crew.py`
      confirma essa abordagem.

    - Passagem de Contexto/Histórico:
        - O contexto relevante da conversa atual ou a solicitação específica do usuário é passada
          para os agentes do CrewAI no momento de sua criação, geralmente através dos parâmetros
          `goal` do `Agent` e `description` da `Task`.
        - Por exemplo, em `crews.email.crew.get_email_crew(user_input)`, a variável `user_input`
          (que contém a solicitação do usuário) é interpolada nas strings de `goal` e `description`.
          `Agent(goal=f"..., based on user request: {user_input}")`
          `Task(description=f"..., based on user request: {user_input}")`

    - Mecanismos de Memória do CrewAI:
        - CrewAI possui funcionalidades de memória que podem ser configuradas para os agentes,
          como `Memory` (e subclasses como `ShortTermMemory`, `LongTermMemory`, `NoMemory`).
          Estas permitem que os agentes lembrem-se de interações passadas dentro de uma mesma execução
          de `crew.kickoff()` ou potencialmente entre execuções se a memória for gerenciada externamente
          e passada para os agentes.
        - No entanto, a implementação atual nos arquivos `crews/*.py` não utiliza explicitamente
          essas classes de memória do CrewAI. A "memória" é efetivamente o contexto fornecido
          na `goal` e `description` da tarefa.

    - Como Melhorar a Memória dos Agentes (se necessário):
        - Para memória de curto prazo dentro de uma única execução de `crew.kickoff()`: A passagem de
          informações detalhadas no `goal` e `description` é a abordagem atual e geralmente eficaz.
          O próprio CrewAI também gerencia o contexto entre tarefas sequenciais dentro de um `Crew`.
        - Para memória de longo prazo entre diferentes `crew.kickoff()`:
            1.  Modificar os scripts em `crews/` para não recriar agentes e tarefas a cada chamada,
                mas sim reutilizar instâncias (isso exigiria um gerenciamento de estado mais complexo).
            2.  Utilizar as classes de memória do CrewAI (ex: `LongTermMemory`) e persistir/carregar
                o estado dessa memória conforme necessário. Isso pode envolver armazenamento em banco de dados
                ou arquivos.
            3.  Passar um resumo do histórico de conversas relevantes (do `ChatManager.conversation_history`)
                para o `goal` ou `description` das tarefas, permitindo que o agente tenha acesso a um
                contexto mais amplo da interação atual. Por exemplo:
                `Task(description=f"User request: {user_input}. Conversation history: {condensed_history}")`
    """
    def __init__(self):
        self.client = get_openai_client() # Use the new client getter
        self.conversation_history = []

    def add_message(self, role: str, content: str):
        """
        Adiciona uma mensagem ao histórico de conversação.
        """
        self.conversation_history.append({"role": role, "content": content})

    def reset_conversation(self):
        """
        Limpa o histórico de conversação.
        """
        self.conversation_history = []

    def get_completion(self, user_input: str) -> Dict:
        """
        Obtém uma resposta do modelo de chat completion para a entrada do usuário.
        Retorna um dicionário com a resposta e informações sobre como processá-la.
        """
        # Adiciona a entrada do usuário ao histórico
        self.add_message("user", user_input)

        # Sistema prompt que define o comportamento do assistente
        system_prompt = """
        Você é um assistente inteligente encarregado de analisar as mensagens do usuário e o histórico da conversa para determinar a melhor forma de processar cada entrada.
        Sua principal tarefa é decidir se responde diretamente ao usuário ou se delega a tarefa a um crew especializado.

        **Considerações Chave:**
        1.  **Histórico da Conversa:** SEMPRE considere o histórico completo da conversa (`conversation_history`) fornecido nas mensagens. As interações anteriores do usuário podem fornecer um contexto crucial para a consulta atual. Por exemplo, se o usuário pediu anteriormente para redigir um email e agora diz 'envie-o', você deve entender esse contexto.
        2.  **Intenção do Usuário:** Analise cuidadosamente a intenção do usuário. Se a solicitação for claramente para uma ferramenta ou serviço específico (como enviar um email ou realizar uma pesquisa na web), delegue ao crew apropriado.
        3.  **Respostas Diretas vs. Delegação:** Se a solicitação for uma pergunta geral, uma saudação, uma pergunta sobre suas capacidades, ou se a intenção não for clara o suficiente para delegar a um crew específico, responda diretamente.

        **Opções de Processamento:**
        1.  **Responder diretamente (`direct_response`):** Para conversas gerais, perguntas sobre suas funcionalidades, saudações, ou quando a solicitação não se encaixa claramente em um dos crews especializados.
        2.  **Encaminhar para um crew especializado (`use_crew`):**
            -   **Crew de Email (`email`):** Use para solicitações como 'Envie um email para joao@exemplo.com sobre nossa reunião de amanhã.', 'Preciso redigir uma mensagem para o cliente X sobre o projeto Y.', 'Rascunhe um email de agradecimento para Maria.'
                -   *Exceção:* Se o usuário perguntar 'Como configuro o email?' ou 'O que é o crew de email?', responda diretamente.
            -   **Crew de Pesquisa (`search`):** Use para solicitações como 'Qual a capital da França?', 'Pesquise as últimas notícias sobre inteligência artificial.', 'Encontre informações sobre o filme Oppenheimer.', 'Busque tutoriais de Python para iniciantes.'
                -   *Exceção:* Se o usuário perguntar 'O que você pode pesquisar?' ou 'Como funciona o crew de pesquisa?', responda diretamente.
            -   **Crew de Calculadora (`calculator`):** Use para solicitações de cálculos matemáticos diretos que envolvam as operações básicas: adição (+), subtração (-), multiplicação (*) e divisão (/). A ferramenta de calculadora atual NÃO suporta parênteses para alterar a ordem das operações, exponenciação ou funções matemáticas complexas.
                -   *Exemplos para `calculator` crew:* 'Quanto é 15 + 3?', 'Calcule 100 * 5', 'Qual o resultado de 45 / 9?', '10 - 2 + 3'
                -   *Exceção:* Se o usuário perguntar 'Você pode fazer matemática?' ou 'Como funciona a calculadora?', responda diretamente. Se a expressão for muito complexa (ex: 'calcule (10+5)*2^3'), responda diretamente informando as limitações da calculadora.
            -   **(Futuros Crews):** Este sistema pode ser expandido com outros crews. Sempre verifique a lista atual de crews disponíveis se a solicitação parecer especializada.

        **Exemplos de Conversa Geral para Resposta Direta (`direct_response`):**
        -   'Olá, como você está?'
        -   'O que você pode fazer?'
        -   'Conte uma piada.'
        -   'Obrigado pela ajuda.'
        -   'Qual o seu propósito?'

        **Tratamento de Ambiguidade:**
        -   Se a solicitação do usuário for ambígua e o histórico da conversa não fornecer clareza suficiente sobre se deve responder diretamente ou usar um crew, você pode fazer uma pergunta de esclarecimento por meio de uma `direct_response`. No entanto, priorize tomar uma decisão se o contexto permitir.

        **Formato da Resposta (JSON OBRIGATÓRIO):**
        Sua resposta DEVE ser um objeto JSON com a seguinte estrutura:
        {
            "action": "direct_response" ou "use_crew",
            "crew_type": null (SE action for "direct_response") OU "email" OU "search" OU "calculator" (SE action for "use_crew"),
            "response": "Sua resposta direta ao usuário." (OBRIGATÓRIO SE action for "direct_response", pode ser uma breve confirmação ou uma pergunta de acompanhamento se action for "use_crew" e você precisar de mais informações antes de delegar, mas geralmente será nulo para "use_crew" se a delegação for direta),
            "explanation": "Uma breve explicação da sua decisão e do raciocínio utilizado, considerando o histórico da conversa e a intenção do usuário."
        }

        **Instruções Adicionais para o Campo `response` no JSON:**
        -   Se `action` for `direct_response`, o campo `response` DEVE conter a sua resposta textual ao usuário.
        -   Se `action` for `use_crew`, o campo `response` geralmente será `null` ou uma mensagem curta como "Entendido, vou encaminhar para o crew de email." se nenhuma informação adicional for necessária do usuário antes da delegação. Se você precisar de esclarecimentos *antes* de delegar (o que deve ser raro), use `direct_response` para fazer a pergunta.

        Analise cuidadosamente a entrada do usuário e o histórico da conversa para tomar a decisão mais apropriada.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            *self.conversation_history
        ]

        # Faz a chamada para a API
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        # Obtém a resposta
        content = response.choices[0].message.content

        # Adiciona a resposta ao histórico
        self.add_message("assistant", content)

        # Analisa o JSON retornado
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            # Fallback caso haja erro no JSON
            return {
                "action": "direct_response",
                "crew_type": None,
                "response": "Desculpe, ocorreu um erro ao processar sua solicitação.",
                "explanation": "Erro ao analisar a resposta JSON."
            }

    def handle_user_input(self, user_input: str) -> Dict:
        """
        Processa a entrada do usuário e decide como responder.
        """
        result = self.get_completion(user_input)

        # Retorna o resultado para ser processado pelo main.py
        return result

# --- Seção de Testes Conceituais ---
# Os testes reais devem ser implementados em um framework de testes como pytest ou unittest,
# preferencialmente em arquivos separados dentro de um diretório 'tests/'.
# Estes testes provavelmente exigirão mocking da chamada à API OpenAI.

# Testes para ChatManager (`tests/test_chat_completion.py`):
# 1. Teste de Delegação para Crew de Calculadora:
#    - Setup:
#      - Instanciar `ChatManager`.
#      - Mockar `chat_manager.client.chat.completions.create` para retornar uma resposta JSON controlada.
#    - Cenários:
#      - Input: "quanto é 2 + 2?"
#        - Mock da API OpenAI para retornar: `{"action": "use_crew", "crew_type": "calculator", "response": null, "explanation": "Solicitação de cálculo."}`
#        - Ação: `chat_manager.handle_user_input("quanto é 2 + 2?")`
#        - Asserção: Verificar se o resultado corresponde ao JSON mockado, especialmente `action` e `crew_type`.
#      - Input: "calcule 10 * 5 / 2"
#        - Mock da API OpenAI para retornar: `{"action": "use_crew", "crew_type": "calculator", "response": null, "explanation": "Cálculo matemático explícito."}`
#        - Ação: `chat_manager.handle_user_input("calcule 10 * 5 / 2")`
#        - Asserção: Resultado esperado.

# 2. Teste de Delegação para Crew de Email:
#    - Setup: Similar ao anterior.
#    - Cenários:
#      - Input: "envie um email para teste@exemplo.com sobre o projeto X"
#        - Mock da API OpenAI para retornar: `{"action": "use_crew", "crew_type": "email", "response": null, "explanation": "Solicitação de envio de email."}`
#        - Ação: `chat_manager.handle_user_input(...)`
#        - Asserção: Resultado esperado.

# 3. Teste de Delegação para Crew de Pesquisa:
#    - Setup: Similar ao anterior.
#    - Cenários:
#      - Input: "quais as últimas notícias sobre IA?"
#        - Mock da API OpenAI para retornar: `{"action": "use_crew", "crew_type": "search", "response": null, "explanation": "Solicitação de pesquisa na web."}`
#        - Ação: `chat_manager.handle_user_input(...)`
#        - Asserção: Resultado esperado.

# 4. Teste de Resposta Direta (Não Delegação):
#    - Setup: Similar.
#    - Cenários:
#      - Input: "olá, tudo bem?"
#        - Mock da API OpenAI para retornar: `{"action": "direct_response", "crew_type": null, "response": "Olá! Tudo bem, e com você?", "explanation": "Saudação geral."}`
#        - Ação: `chat_manager.handle_user_input("olá, tudo bem?")`
#        - Asserção: Resultado esperado.
#      - Input: "o que é o crew de calculadora?" (deve ser tratado pela exceção no prompt)
#        - Mock da API OpenAI para retornar: `{"action": "direct_response", "crew_type": null, "response": "O crew de calculadora serve para realizar cálculos matemáticos básicos.", "explanation": "Pergunta sobre funcionalidade."}`
#        - Ação: `chat_manager.handle_user_input("o que é o crew de calculadora?")`
#        - Asserção: Resultado esperado.
#      - Input: "calcule (10+5)*2^3" (expressão complexa, deve ser tratada pela exceção no prompt)
#        - Mock da API OpenAI para retornar: `{"action": "direct_response", "crew_type": null, "response": "Desculpe, a calculadora atual só suporta operações básicas (+, -, *, /) e não lida com parênteses ou exponenciação.", "explanation": "Cálculo complexo não suportado."}`
#        - Ação: `chat_manager.handle_user_input("calcule (10+5)*2^3")`
#        - Asserção: Resultado esperado.

# 5. Teste de Histórico de Conversa Influenciando Decisão (Mais Avançado):
#    - Setup:
#      - Adicionar mensagens ao `chat_manager.conversation_history`.
#      - Ex: `chat_manager.add_message("user", "Preciso calcular 10 * 20")`
#      - Mockar a API para retornar `{"action": "use_crew", "crew_type": "calculator", ...}` para a primeira mensagem.
#      - `chat_manager.add_message("assistant", json.dumps({"action": "use_crew", ...}))` (simulando a resposta do LLM)
#      - `chat_manager.add_message("user", "e quanto é 5 + 7?")` (segunda mensagem do usuário)
#    - Ação: Chamar `chat_manager.handle_user_input("e quanto é 5 + 7?")`
#    - Mock da API OpenAI para a segunda chamada, esperando que o LLM ainda delegue para "calculator".
#    - Asserção: Verificar se a decisão para a segunda mensagem ainda é `use_crew` e `calculator`, mostrando que o LLM (mockado) está usando o histórico.

# 6. Teste de Fallback de Erro JSON:
#    - Setup:
#      - Mockar `chat_manager.client.chat.completions.create` para retornar uma string que NÃO é JSON válido.
#    - Ação: `chat_manager.handle_user_input("qualquer entrada")`
#    - Asserção: Verificar se o resultado é o dicionário de fallback definido no bloco `except json.JSONDecodeError`.
