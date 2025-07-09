"""
agent.py

Este módulo define a classe Agent, responsável por gerenciar a interação entre um
modelo de linguagem (LLM), o histórico da conversa (memória) e ferramentas externas.
O agente processa mensagens do usuário, decide quando invocar ferramentas, integra
as respostas dessas ferramentas ao contexto e retorna respostas refinadas ao usuário.

A classe Agent foi projetada para ser extensível e robusta, permitindo integração
dinâmica com múltiplas ferramentas e garantindo o controle do fluxo de execução,
mesmo em cenários recursivos de múltiplas chamadas de ferramentas.
"""

import json
from typing import TYPE_CHECKING, Any

try:
    from openai import OpenAIError
except ImportError:
    OpenAIError = type("OpenAIError", (Exception,), {})

from memory.memory import Memory
from tools.tool import Tool

if TYPE_CHECKING:
    from openai import OpenAI
    from openai.types.chat import ChatCompletionMessage




class Agent:
    """
    Um agente inteligente que interage com usuários, mantém o histórico da conversa e
    executa ferramentas externas de forma dinâmica e recursiva, integrando suas
    respostas ao contexto para fornecer respostas mais precisas.

    O agente utiliza um modelo de linguagem (LLM) para interpretar as mensagens do
    usuário, decidir quando invocar ferramentas e refinar suas respostas com base nos
    resultados dessas ferramentas.
    """

    def __init__(
        self,
        client: "OpenAI",
        tools: list[Tool] | None = None,
        name: str = "AI Agent",
        role: str = "Personal Assistant",
        instructions: str = "Help users with any question",
        model: str = "gpt-4.1",
        temperature: float = 0.0,
    ) -> None:
        """
        Inicializa o agente com o cliente LLM, ferramentas, configurações e histórico
        de memória.

        Args:
            client (OpenAI): Cliente para comunicação com o modelo de linguagem.
            tools (Optional[List[Tool]]): Lista de ferramentas disponíveis para o
                agente.
            name (str): Nome do agente.
            role (str): Papel ou função do agente.
            instructions (str): Instruções iniciais para o agente.
            model (str): Nome do modelo de linguagem a ser utilizado.
            temperature (float): Temperatura do modelo (controla a criatividade das
                respostas).
        """
        self.client = client
        self.name = name
        self.role = role
        self.instructions = instructions
        self.model = model
        self.temperature = temperature
        self.memory = Memory()
        self.memory.add_message(
            role="system",
            content=f"You're an AI Agent, your role is {self.role}, "
            f"and you need to {self.instructions}",
        )
        self.tools = tools or []
        self.tool_map = {t.name: t for t in self.tools}
        #* Certifique-se de que todas as ferramentas implementam to_openai_spec
        #* corretamente
        tools_list = [t.to_openai_spec() for t in self.tools] if self.tools else None
        self.openai_tools: list[dict[str, Any]] | None = (
            tools_list if tools_list else None
        )

    def invoke(self, user_message: str) -> str:
        """
        Processa a mensagem do usuário, gera uma resposta do modelo de linguagem e
        executa ferramentas se necessário.

        O método adiciona a mensagem do usuário ao histórico, solicita uma resposta ao
        modelo de linguagem, verifica se há chamadas de ferramentas sugeridas, executa
        essas ferramentas (de forma recursiva, se necessário) e retorna a resposta
        final ao usuário.

        Args:
            user_message (str): Mensagem enviada pelo usuário.

        Returns:
            str: Resposta final do agente ao usuário.
        """
        self.memory.add_message(role="user", content=user_message)

        # Cast explícito para evitar erro de tipo
        # Converter mensagens para o formato esperado pela OpenAI API
        messages_for_openai = []
        for m in self.memory.messages:
            msg = {k: v for k, v in m.items() if v is not None}
            # tool_calls deve ser omitido se não for dict
            if "tool_calls" in msg and not isinstance(msg["tool_calls"], dict):
                del msg["tool_calls"]
            messages_for_openai.append(msg)  # type: ignore
        # Só passar tools se houver ferramentas
        kwargs = {"messages": messages_for_openai}  # type: ignore
        if self.openai_tools:
            kwargs["tools"] = self.openai_tools
        ai_message = self._get_completion(**kwargs)  # type: ignore

        tool_calls = getattr(ai_message, "tool_calls", None)
        self.memory.add_message(
            role="assistant",
            content=str(ai_message.content) if ai_message.content is not None else "",
            tool_calls=tool_calls,
        )

        if tool_calls:
            self._call_tools(tool_calls)

        last_msg = self.memory.last_message()
        if last_msg:
            msg_dict = dict(last_msg)
            if "content" in msg_dict and isinstance(msg_dict["content"], str):
                return msg_dict["content"]
            if "content" in msg_dict:
                return str(msg_dict["content"])
        return ""

    def _call_tools(
        self,
        tool_calls: list[Any],
        recursion_depth: int = 0,
        max_depth: int = 5,
    ) -> None:
        """
        Executa as ferramentas solicitadas pela IA e integra as respostas ao histórico
        da conversa.

        O método é recursivo e permite múltiplas chamadas de ferramentas em sequência,
        limitando a profundidade para evitar loops infinitos.

        Args:
            tool_calls (List[Any]): Lista de chamadas de ferramentas sugeridas pela IA.
            recursion_depth (int): Profundidade atual da recursão.
            max_depth (int): Profundidade máxima permitida para evitar loops infinitos.

        Raises:
            RuntimeError: Se o limite de recursão for atingido.
        """
        error_msg = "Limite de recursão de ferramentas atingido."
        if recursion_depth > max_depth:
            raise RuntimeError(error_msg)

        for t in tool_calls:
            tool_call_id = t.id
            function_name = t.function.name
            args = json.loads(t.function.arguments)
            callable_tool = self.tool_map.get(function_name)
            if not callable_tool:
                self.memory.add_message(
                    role="tool",
                    content=f"Tool '{function_name}' not found.",
                    tool_call_id=tool_call_id,
                )
                continue
            try:
                result = callable_tool(**args)
            except Exception as e:  # noqa: BLE001
                result = f"Erro ao executar a ferramenta: {e}"
            self.memory.add_message(
                role="tool", content=str(result), tool_call_id=tool_call_id
            )

        # Converter mensagens para o formato esperado pela OpenAI API
        messages_for_openai = []
        for m in self.memory.messages:
            msg = {k: v for k, v in m.items() if v is not None}
            # tool_calls deve ser omitido se não for dict
            if "tool_calls" in msg and not isinstance(msg["tool_calls"], dict):
                del msg["tool_calls"]
            messages_for_openai.append(msg)  # type: ignore
        # Só passar tools se houver ferramentas
        kwargs = {"messages": messages_for_openai}  # type: ignore
        if self.openai_tools:
            kwargs["tools"] = self.openai_tools
        ai_message = self._get_completion(**kwargs)  # type: ignore

        tool_calls = getattr(ai_message, "tool_calls", None)  # type: ignore

        # tool_calls pode ser None ou uma lista, mas add_message espera dict ou None
        tc = tool_calls if isinstance(tool_calls, dict) else None
        self.memory.add_message(
            role="assistant",
            content=str(ai_message.content) if ai_message.content is not None else "",
            tool_calls=tc,
        )

        if tool_calls:
            self._call_tools(tool_calls, recursion_depth + 1, max_depth)

    def _get_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> "ChatCompletionMessage":
        """
        Chama o modelo de linguagem para obter a próxima resposta, considerando o
        histórico da conversa e as ferramentas disponíveis.

        Args:
            messages (List[Dict[str, Any]]): Histórico de mensagens da conversa.

        Returns:
            ChatCompletionMessage: Mensagem de resposta do modelo de linguagem.

        Raises:
            RuntimeError: Se houver erro ao chamar o modelo.
        """
        try:
            params = {
                "model": self.model,
                "temperature": self.temperature,
                "messages": messages,
            }
            if tools:
                params["tools"] = tools
            response = self.client.chat.completions.create(**params)  # type: ignore
            return response.choices[0].message  # type: ignore
        except OpenAIError as error:
            msg = f"Erro ao chamar o modelo: {error}"
            raise RuntimeError(msg) from error
