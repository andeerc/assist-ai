#!/usr/bin/env python3
from openai import OpenAI
from config.settings import OPENAI_API_KEY
from typing import Dict, List, Optional
import json

class ChatManager:
    """
    Gerencia a interação com o usuário usando o modelo de chat completion da OpenAI.
    Determina quando acionar um crew específico com base na entrada do usuário.
    """
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
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
        Você é um assistente que ajuda a determinar como processar a entrada do usuário.
        Sua tarefa é analisar a mensagem do usuário e decidir se deve responder diretamente ou encaminhar para um crew especializado.
        Você deve considerar o seguinte:
        - Se a mensagem do usuário parece ser uma solicitação para alguma ferramenta ou serviço específico (como enviar um email ou realizar uma pesquisa na web), você deve encaminhar para o crew especializado.
        - Caso contrário, responda diretamente ao usuário com uma conversa normal.

        Analise a entrada do usuário e determine se deve:
        1. Responder diretamente com uma conversa normal
        2. Encaminhar para um crew especializado:
           - "email" - para envio de emails
           - "search" - para pesquisas na web e busca de informações atualizadas

        Responda em JSON com o seguinte formato:
        {
            "action": "direct_response" ou "use_crew",
            "crew_type": null ou "email" ou "search" (apenas se action for "use_crew"),
            "response": "Sua resposta direta ao usuário" (apenas se action for "direct_response"),
            "explanation": "Explicação da sua decisão"
        }

        Exemplos do tipo de mensagem que deve ser enviada para cada crew:
        - Crew de email: "Envie um email para fulano@exemplo.com", "Preciso mandar um email para meu chefe"
        - Crew de pesquisa: "Pesquise sobre o clima em São Paulo", "Quais são as últimas notícias sobre IA?", "Procure informações sobre o lançamento do iPhone 15"

        Para outros tipos de interações, responda diretamente ao usuário.
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
