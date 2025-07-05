def chat_with_tools(
    client: OpenAI,
    user_question: str = None,
    memory: Memory = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.0,
    tools: list = None,
) -> str:
    """Executa uma conversa com AI agent que pode usar ferramentas (function calling).

    Esta função é o "cérebro" da interação com AI agents. Ela pega sua pergunta,
    consulta o histórico da conversa (se houver), envia tudo para o modelo OpenAI,
    e retorna a resposta do AI. O modelo pode decidir usar ferramentas durante
    a conversa para obter informações adicionais.

    **Conceitos importantes para iniciantes:**
    - **Injeção de Dependência**: Cliente é passado como parâmetro (boa prática)
    - **Function Calling**: Capacidade do AI de "chamar" ferramentas externas
    - **Memory**: Histórico da conversa que dá contexto ao AI
    - **Tools**: Lista de ferramentas/funções que o AI pode usar
    - **Temperature**: Controla criatividade (0.0 = determinístico, 1.0 = criativo)

    **Por que cliente como parâmetro?**
    - Evita dependência de variáveis globais (má prática)
    - Facilita testes unitários (pode passar mock do cliente)
    - Torna a função mais flexível e reutilizável
    - Segue princípios de Clean Code e SOLID
    - Permite usar diferentes configurações de cliente

    **Como funciona o fluxo:**
    1. Recebe cliente OpenAI configurado como parâmetro
    2. Adiciona pergunta na memória (se fornecida)
    3. Prepara mensagens (pergunta atual + histórico da Memory)
    4. Envia para OpenAI via cliente com lista de ferramentas
    5. AI decide se precisa usar ferramentas ou responder diretamente
    6. Salva resposta do AI na memória (incluindo tool_calls)
    7. Retorna resposta em texto

    Args:
        client (OpenAI): Instância configurada do cliente OpenAI.
                        Obtida via OpenAIClient.get_client().
                        OBRIGATÓRIO - deve ser o primeiro parâmetro.
        user_question (str, optional): Sua pergunta ou mensagem para o AI.
                                        Se None, usa apenas histórico da memória.
                                        Defaults to None.
        memory (Memory, optional): Instância da classe Memory contendo histórico.
                                    Se None, trata como conversa nova sem contexto.
                                    Defaults to None.
        model (str, optional): Nome do modelo OpenAI a usar.
                                Defaults to "gpt-4o-mini".
        temperature (float, optional): Controla aleatoriedade (0.0 a 1.0).
                                        Defaults to 0.0.
        tools (list, optional): Lista de ferramentas no formato OpenAI.
                                Defaults to None.

    Returns:
        str: Resposta textual do AI assistant. Verifique tool_calls na memória
                para detectar se ferramentas foram solicitadas.

    Raises:
        TypeError: Se client não for uma instância válida do OpenAI.
        OpenAIError: Se houver problemas na comunicação com a API.
        ValueError: Se parâmetros estiverem em formato inválido.

    Examples:
        Setup e uso básico:
        >>> # Configuração (feita uma vez)
        >>> api_loader = ApiKeyLoader(Path(".env"))
        >>> openai_client = OpenAIClient(api_loader.get_openai_key())
        >>> client = openai_client.get_client()
        >>>
        >>> # Uso da função (cliente sempre como primeiro parâmetro)
        >>> resposta = chat_with_tools(client, "Olá, como você está?")
        >>> print(resposta)

        Com memória e ferramentas:
        >>> memory = Memory()
        >>> tools = [{"type": "function", "function": {"name": "get_weather", ...}}]
        >>>
        >>> resposta = chat_with_tools(
        ...     client,  # Sempre primeiro parâmetro
        ...     user_question="Qual o clima em SP?",
        ...     memory=memory,
        ...     tools=tools
        ... )

        Diferentes configurações de cliente:
        >>> # Cliente para desenvolvimento (temperatura alta)
        >>> dev_client = OpenAIClient(api_key, temperature=0.8).get_client()
        >>>
        >>> # Cliente para produção (temperatura baixa)
        >>> prod_client = OpenAIClient(api_key, temperature=0.0).get_client()
        >>>
        >>> # Usando clientes diferentes
        >>> resp_criativa = chat_with_tools(dev_client, "Conte uma piada")
        >>> resp_precisa = chat_with_tools(prod_client, "Quanto é 2+2?")


    Note:
        - Cliente deve ser sempre o primeiro parâmetro (obrigatório)
        - Evita dependências globais - mais limpo e testável
        - Permite reutilizar a função com diferentes configurações
        - Facilita mocking para testes unitários
    """
    # Validação do cliente
    if not hasattr(client, "chat") or not hasattr(client.chat, "completions"):
        raise TypeError("client must be a valid OpenAI client instance")

    # Preparação das mensagens
    messages = [{"role": "user", "content": user_question}]

    if memory:
        if user_question:
            memory.add_message(role="user", content=user_question)
        messages = memory.get_messages()

    # Chamada para a API OpenAI usando o cliente fornecido
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages,
        tools=tools,
    )

    # Extração da resposta
    ai_message = str(response.choices[0].message.content)
    tool_calls = response.choices[0].message.tool_calls

    # Salva na memória se fornecida
    if memory:
        memory.add_message(role="assistant", content=ai_message, tool_calls=tool_calls)

    return ai_message

if __name__ == "__main__":
    #* Verificando a assinatura da função:
    import inspect
    signature = inspect.signature(chat_with_tools)
    print(f"A assinatura da função chat_with_tools é: \n{signature}")
