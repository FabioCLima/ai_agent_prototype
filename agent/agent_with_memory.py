"""
This module shows how to solve the inherent statelessness of Large Language
Models (LLMs) by implementing a simple memory system. Managing the conversation
history, the agent can simulate remembering past interactions and provide coherent
multi-turn conversations.

In the simple AI agent, the memory is a list[ChatCompletionMessageParam] such:
memory = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is an API?"}
]

A basic message list is used to maintain conversation history.
Each interaction is appended to this list:
    * system message to set behavior :
        {"role": "system", "content": f"{self.role} {self.instructions}"}

    * user messages:
        {"role": "user", "content": message}

    * assistant responses:
        response.choices[0].message.content

In order to create an abstraction, to manage messages more cleanly.
The class Memory provides:
    * add_message(role, content): Adds a message
    * get_messages(): Retrieves the full memory list

The __init__ method initializes the an empty memory list.

A enhaced chat function should be built to interact with the LLM using the Memory
instance.

    > Adds the user message to memory,
    > calls the LLM with the full message history,
    > Appends the LLM response back to memory,
    > Returns the new assistant message.

The initial system message is set manually.
    . User: "The capital of Brazil is Brasilia"
    . Follow-Up: "What have I asked?."

The agent correctly remembers the user's question using the built memory.
"""

#! IMPORTS EXTERNOS - Bibliotecas padrão e de terceiros
from pathlib import Path
from typing import Literal

from openai.types.chat.chat_completion import ChatCompletion
#! IMPORTS INTERNOS - Classes do nosso módulo
from simple_ai_agent import Agent, ApiKeyLoader, OpenAIClient


#! CLASSE MEMORY - Abstração para gerenciar a memória da conversa
class Memory:
    """Gerencia o histórico de mensagens para conversas com LLMs.

    Esta classe fornece uma abstração simples para manter o histórico de
    conversas entre usuário e assistente, permitindo que o agente "lembre"
    de interações anteriores.

    A memória armazena mensagens no formato esperado pela API da OpenAI:
    List[Dict[str, str]], onde cada mensagem é um dicionário com 'role'
    e 'content'.

    Attributes:
        messages (List[Dict[str, str]]): Lista de mensagens armazenadas
            na memória. Cada mensagem é um dicionário com 'role' (str)
            e 'content' (str).

    Example:
        >>> memory = Memory()
        >>> memory.add_message("system", "You are a helpful assistant.")
        >>> memory.add_message("user", "What is Python?")
        >>> memory.add_message("assistant", "Python is a programming language.")
        >>> messages = memory.get_messages()
        >>> print(len(messages))  # 3
        >>> print(messages[1]["content"])  # "What is Python?"
    """

    def __init__(self):
        """Inicializa a memória com uma lista vazia de mensagens.

        Example:
            >>> memory = Memory()
            >>> print(len(memory.get_messages()))  # 0
        """
        self.messages: list[dict[str, str]] = []

    def add_message(self, role: Literal["user", "system", "assistant"], content: str):
        """Adiciona uma nova mensagem ao histórico de memória.

        Args:
            role: Papel da mensagem. Deve ser um dos valores:
                - "system": Mensagem do sistema (contexto/comportamento)
                - "user": Mensagem do usuário
                - "assistant": Resposta do assistente
            content: Conteúdo da mensagem.

        Example:
            >>> memory = Memory()
            >>> memory.add_message("user", "Hello, how are you?")
            >>> memory.add_message("assistant", "I'm doing well, thank you!")
            >>> messages = memory.get_messages()
            >>> print(len(messages))  # 2
            >>> print(messages[0]["role"])  # "user"
            >>> print(messages[1]["content"])  # "I'm doing well, thank you!"
        """
        self.messages.append({"role": role, "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        """Retorna a lista completa de mensagens armazenadas na memória.

        Returns:
            List[Dict[str, str]]: Lista de mensagens no formato
                esperado pela API da OpenAI. Cada mensagem é um dicionário
                com 'role' e 'content'.

        Example:
            >>> memory = Memory()
            >>> memory.add_message("user", "What is 2+2?")
            >>> memory.add_message("assistant", "2+2 equals 4.")
            >>> messages = memory.get_messages()
            >>> for msg in messages:
            ...     print(f"{msg['role']}: {msg['content']}")
            user: What is 2+2?
            assistant: 2+2 equals 4.
        """
        return self.messages


#! CLASSE MEMORYAGENT - Agente com capacidade de memória
# TODO: Criar classe que herda de Agent e usa Memory


class AgentWithMemory(Agent):  # Herda da classe Agent
    def __init__(
        self,
        client,
        name="AI Agent",
        role="You are a helpful assistant.",
        instructions="help the users with any question",
        model="gpt-4.1",
        temperature=0.0,
    ):
        # *1. Chama o construtor da classe pai (Agent)
        super().__init__(client, name, role, instructions, model, temperature)

        # * Adiciona funcionalidade de memória - instância a classe Memory
        self.memory = Memory()

        # * Adiciona a mensagem inicial do sistema - Contexto do agente
        system_message = f"{self.role} {self.instructions}"
        self.memory.add_message("system", system_message)

    def invoke(self, message: str) -> str:
        """
        Envia uma mensagem ao modelo mantendo o histórico de conversas

        Args:
            message (str): A mensagem do usuário.

        Returns:
            str: A resposta do modelo.
        """

        # * 1.Adiciona a mensagem do usuário à memória
        self.memory.add_message("user", message)

        # * 2.Obtém o histórico completo de mensagens
        messages = self.memory.get_messages()

        # * 3.Chama LLM com o histórico completo
        response: ChatCompletion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore # Envia TODAS as mensagens
            temperature=self.temperature,
        )

        # * 4.Extrai resposta
        result: str = response.choices[0].message.content or ""

        # * 5.Adiciona resposta à memória
        self.memory.add_message("assistant", result)

        return result


#! EXEMPLO DE USO E TESTES
if __name__ == "__main__":
    # * CONFIGURAÇÃO INICIAL - Carregar chave da API
    env_path = Path(__file__).resolve().parent / ".env"
    api_loader = ApiKeyLoader(env_path)
    openai_key = api_loader.get_openai_key()

    # * CRIAÇÃO DO CLIENTE - Instanciar cliente OpenAI
    openai_client = OpenAIClient(openai_key)
    client = openai_client.get_client()

    # * CRIAÇÃO DO AGENTE - Instanciar agente básico
    ai_agent = Agent(client)

    # ? Como implementar a funcionalidade de memória?
    # TODO: Criar instância de MemoryAgent e testar conversação multi-turn
    # * Instanciando a classe Memory
    memory = Memory()
    memory.add_message("system", "You are a helpful assistant.")
    memory.add_message("user", "What is the capital of Brazil?")
    messages = memory.get_messages()
    print(messages)

    agent = AgentWithMemory(client)
    response1 = agent.invoke("What is the capital of Brazil?")
    response2 = agent.invoke("What have I asked?")
    print(response1)
    print(response2)