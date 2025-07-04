# ai_agent_prototype/memoory/memory_v2.py
"""
Memory class for storing and managing messages in a conversation.
"""

from typing import Any, Literal, NotRequired, TypedDict


class Message(TypedDict):
    """
    A TypedDict representing a message exchanged in the system.
    Attributes:
        role (Literal["user", "system", "assistant", "tool"]):
            The role of the message sender, which can be one of "user", "system",
            "assistant", or "tool".
        content (str):
            The textual content of the message.
        tool_calls (dict[str, Any], optional):
            A dictionary containing information about tool calls associated with the
            message.
        tool_call_id (str, optional):
            An identifier for the tool call related to this message.
    """

    role: Literal["user", "system", "assistant", "tool"]
    content: str
    tool_calls: NotRequired[dict[str, Any]]
    tool_call_id: NotRequired[str]


class Memory:
    """Manages the message history of a conversation with an AI agent.

    This class is responsible for storing, retrieving, and managing messages
    exchanged between users, systems, assistants, and tools during an
    AI conversation session.

    Attributes:
        _messages: Private list storing all conversation messages.

    Example:
        >>> memory = Memory()
        >>> memory.add_message("user", "Hello, how are you?")
        >>> memory.add_message("assistant", "Hi! I'm doing well, thank you.")
        >>> messages = memory.get_messages()
        >>> print(len(messages))  # 2
    """

    def __init__(self) -> None:
        """Initializes a new instance of the Memory class.

        Creates an empty list to store conversation messages.
        """
        self._messages: list[Message] = []

    def add_message(
        self,
        role: Literal["user", "system", "assistant", "tool"],
        content: str,
        tool_calls: dict[str, Any] | None = None,
        tool_call_id: str | None = None,
    ) -> None:
        """Adds a new message to the conversation history.

        Args:
            role: The role of the entity sending the message. Can be:
                - 'user': User message
                - 'system': System message
                - 'assistant': AI assistant message
                - 'tool': External tool response
            content: The textual content of the message.
            tool_calls: Optional dictionary containing tool call information,
                typically when the assistant requests tool execution.
                Defaults to None.
            tool_call_id: Unique identifier for the tool call.
                Required when role='tool'. Defaults to None.

        Raises:
            ValueError: If role='tool' but no tool_call_id is provided.

        Example:
            >>> memory = Memory()
            >>> memory.add_message("user", "What's the square root of 16?")
            >>> memory.add_message(
            ...     "assistant",
            ...     "I'll calculate that for you.",
            ...     tool_calls={
            ...         "name": "calculator",
            ...         "args": {"operation": "sqrt", "value": 16}
            ...     }
            ... )
            >>> memory.add_message("tool", "4.0", tool_call_id="call_123")
        """
        if role == "tool" and tool_call_id is None:
            msg = "tool_call_id is required for tool messages"
            raise ValueError(msg)

        message: Message = {
            "role": role,
            "content": content,
        }

        if role == "tool":
            # tool_call_id is guaranteed to be not None here due to the check above
            message["tool_call_id"] = str(tool_call_id)
        else:
            if tool_calls is not None:
                message["tool_calls"] = tool_calls

        self._messages.append(message)

    def get_messages(self) -> list[Message]:
        """Returns all messages stored in memory.

        Returns:
            A list containing all stored message dictionaries.
            Each dictionary contains 'role', 'content' keys and optionally
            'tool_calls' or 'tool_call_id'.

        Example:
            >>> memory = Memory()
            >>> memory.add_message("user", "Hello")
            >>> messages = memory.get_messages()
            >>> print(messages[0]['role'])  # 'user'
            >>> print(messages[0]['content'])  # 'Hello'
        """
        return self._messages.copy()  # Return copy to prevent external modification

    def last_message(self) -> Message | None:
        """Returns the last message added to memory.

        Returns:
            A dictionary containing the last message if it exists,
            otherwise returns None.

        Example:
            >>> memory = Memory()
            >>> print(memory.last_message())  # None
            >>> memory.add_message("user", "First message")
            >>> memory.add_message("assistant", "Second message")
            >>> last = memory.last_message()
            >>> print(last['content'])  # 'Second message'
        """
        return self._messages[-1] if self._messages else None

    def reset(self) -> None:
        """Clears all messages from memory.

        Removes all stored messages, resetting the conversation.
        This operation is irreversible.

        Example:
            >>> memory = Memory()
            >>> memory.add_message("user", "Hello")
            >>> print(len(memory.get_messages()))  # 1
            >>> memory.reset()
            >>> print(len(memory.get_messages()))  # 0
        """
        self._messages = []


if __name__ == "__main__":
    # * Criar instancia da classe Memory
    memory = Memory()

    # * Adicionar mensagens à memória
    print(memory.last_message())  # * Checando que o histórico de msg está vazio.
    memory.add_message("user", "What's the square root of 16?")
    memory.add_message(
        "assistant",
        "I'll calculate that for you.",
        tool_calls={
            "name": "calculator",
            "args": {"operation": "sqrt", "value": 16},
        },
    )
    print(memory.last_message())  # * Checando se a mensagem foi adicionada.
    memory.reset()  # * Resetando a memória.
    memory.add_message("tool", "4.0", tool_call_id="call_123")
    print(memory.get_messages())
