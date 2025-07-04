"""
Este módulo define uma classe Memory que é usada para:
- Adicionar novas mensagens.     >> memory.add_message()
- Recuperar todas as mensagens.  >> memory.get_messages() #* @property
- Recuperar a última mensagem.   >> memory.last_message()
- Limpar todas as mensagens      >> memory.reset()

Messages w/history:
[
    {"role":"system", "content":"You are a helpful assistant."},
    {"role":"user", "content":"What is the capital of France?"},

    {"role":"assistant", "content":"The capital of France is Paris."},
    {"role":"user", "content":"What is an interesting fact about Paris?"},
]
************************************************************************
Manages a conversation memory with typed message storage and retrieval.

This module provides a Memory class for handling conversation messages with support for
different roles (user, system, assistant, tool) and optional tool-related metadata.

Key features:
- Add messages with role-based validation
- Retrieve full message history
- Access the last message
- Reset message history
"""

from typing import Any, Literal, NotRequired, TypedDict


class Message(TypedDict):
    """Representa uma mensagem trocada no sistema com tipagem forte.

    Attributes:
        role: Papel do remetente da mensagem. Deve ser um dos: 'user', 'system',
        'assistant' ou 'tool'.
        content: Conteúdo textual da mensagem.
        tool_calls: Informações sobre chamadas de ferramentas (opcional).
        tool_call_id: Identificador para chamada de ferramenta relacionada (opcional).

    Examples:
        >>> msg: Message = {"role": "user", "content": "Olá, mundo!"}
        >>> tool_msg: Message = {"role": "tool", "content": "42",
        "tool_call_id": "call_123"}
    """

    role: Literal["user", "system", "assistant", "tool"]
    content: str
    tool_calls: NotRequired[dict[str, Any]]
    tool_call_id: NotRequired[str]


class Memory:
    """Gerencia o histórico de mensagens de uma conversa com suporte a múltiplos papéis.

    A classe permite armazenar, recuperar e gerenciar mensagens de conversação com
    validação de tipos e estrutura. Mantém um histórico completo da conversa com
    possibilidade de reset.

    Attributes:
        messages: Lista copiada de todas as mensagens armazenadas (property).

    Examples:
        >>> memory = Memory()
        >>> memory.add_message(role="user", content="Oi")
        >>> memory.last_message()
        {'role': 'user', 'content': 'Oi'}
    """

    def __init__(self) -> None:
        """Inicializa uma nova instância de Memory com lista vazia de mensagens."""
        self._messages: list[Message] = []

    def add_message(
        self,
        role: Literal["user", "system", "assistant", "tool"],
        content: str,
        tool_calls: dict[str, Any] | None = None,
        tool_call_id: str | None = None,
    ) -> None:
        """Adiciona uma nova mensagem ao histórico.

        Args:
            role: Papel do remetente ('user', 'system', 'assistant' ou 'tool').
            content: Texto da mensagem.
            tool_calls: Dados de chamadas de ferramentas (opcional).
            tool_call_id: ID de chamada de ferramenta (obrigatório para role='tool').

        Raises:
            ValueError: Se role for 'tool' e tool_call_id não for fornecido.

        Examples:
            >>> memory.add_message("user", "Olá")
            >>> memory.add_message("tool", "result", tool_call_id="123")
        """
        # * Validação para os tipos permitidos de 'role'
        if role not in ["user", "system", "assistant", "tool"]:
            error_msg = f"Invalid role: {role}"
            raise ValueError(error_msg)

        # * Validação para o caso de 'role' ser 'tool'
        if role == "tool" and tool_call_id is None:
            error_msg = "tool_call_id is required for tool messages"
            raise ValueError(error_msg)

        message: Message = {"role": role, "content": content}

        if role == "tool":
            message["tool_call_id"] = str(tool_call_id)
        if tool_calls is not None:
            message["tool_calls"] = tool_calls

        self._messages.append(message)

    @property
    def messages(self) -> list[Message]:
        """Obtém uma cópia segura de todas as mensagens armazenadas.

        Returns:
            Lista copiada de todas as mensagens no histórico.
        """
        return self._messages.copy()

    def last_message(self) -> Message | None:
        """Recupera a última mensagem adicionada ao histórico.

        Returns:
            A última mensagem ou None se o histórico estiver vazio.
        """
        return self._messages[-1] if self._messages else None

    def reset(self) -> None:
        """Limpa completamente o histórico de mensagens."""
        self._messages = []

    def __repr__(self) -> str:
        """Representação oficial do objeto Memory.

        Returns:
            String representando o objeto Memory e seu conteúdo.
        """
        return f"Memory(messages={self._messages})" if self._messages else "Memory()"


if __name__ == "__main__":
    # * Exemplo de demonstração e teste da classe Memory
    # * 1. Criar instância da classe Memory
    memory = Memory()
    print("Memória inicializada.")
    print(f"Última mensagem: {memory.last_message()}")  # Deve ser None

    # * 2. Adicionar mensagens à memória
    print("\nAdicionando mensagens...")
    memory.add_message(role="system", content="Você é um assistente prestativo.")
    memory.add_message(role="user", content="Qual a raiz quadrada de 16?")
    memory.add_message(
        role="assistant",
        content="Eu posso calcular isso para você.",
        tool_calls={
            "name": "calculator",
            "args": {"operation": "sqrt", "value": 16},
        },
    )
    memory.add_message(role="tool", content="4.0", tool_call_id="call_123")

    # * 3. Verificar o estado da memória
    print(f"Última mensagem: {memory.last_message()}")
    all_messages = memory.messages  # Usando a property diretamente
    print(f"Total de mensagens: {len(all_messages)}")
    print("Histórico completo:")
    for msg in all_messages:
        print(f"- {msg}")

    # * 4. Testar a imutabilidade da property messages
    messages_copy = memory.messages
    messages_copy.append({"role": "user", "content": "Mensagem falsa"})
    print(f"\nTotal de mensagens na cópia: {len(messages_copy)}")
    print(f"Total de mensagens na memória original: {len(memory.messages)}")

    # * 5. Resetar a memória
    print("\nResetando a memória...")
    memory.reset()
    print(f"Última mensagem após reset: {memory.last_message()}")  # Deve ser None
    print(f"Total de mensagens após reset: {len(memory.messages)}")

    # * 6. Testar exceção para mensagem tool sem tool_call_id
    try:
        print("\nTestando exceção para 'tool' sem 'tool_call_id'...")
        memory.add_message(role="tool", content="resultado")
    except ValueError as e:
        print(f"Exceção capturada com sucesso: {e}")
