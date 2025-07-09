from typing import List, Optional

from llm_client.openai_client import OpenAIClient
from memory.memory import Memory
from tools.tool import Tool


class AgentAI:
    """
    Orquestrador principal do agente de IA.
    Integra LLM, tools e memória conversacional.

    Args:
        llm_client (OpenAIClient): Cliente para acesso ao modelo LLM.
        tools (List[Tool]): Lista de ferramentas disponíveis para o agente.
        memory (Memory): Instância de memória para histórico de mensagens.
    """
    def __init__(self, llm_client: OpenAIClient, tools: Optional[List[Tool]] = None, memory: Optional[Memory] = None):
        self.llm_client = llm_client
        self.tools = tools or []
        self.memory = memory or Memory()

    def invoke(self, user_input: str) -> str:
        """
        Processa a entrada do usuário, consulta a memória, usa tools se necessário e retorna a resposta.
        (Implementação simplificada para protótipo; pode ser expandida para function calling.)
        """
        # 1. Adiciona a mensagem do usuário na memória
        self.memory.add_message(role="user", content=user_input)

        # 2. Monta o histórico para o LLM (apenas roles válidos e campos aceitos)
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in self.memory.messages
            if m["role"] in ("system", "user", "assistant")
        ]

        # 3. Chama o LLM (exemplo simplificado, sem function calling)
        response = self.llm_client.client.chat.completions.create(
            model="gpt-4o",
            messages=messages  # type: ignore
        )
        answer = response.choices[0].message.content or ""

        # 4. Adiciona resposta do assistente na memória
        self.memory.add_message(role="assistant", content=answer)

        return answer 