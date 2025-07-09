#ai_agents_langchain_langraph/ai_agent_memory_reflection.py

'''
Neste módulo, vamos atualizar o agent de IA:
    - Uma camada de memória para rastrear as interações anteriores.
    - Um mecanismo de auto-reflexão que critica e refina as respostas.

O Agente deve:
    - Armazenar o histórico de conversa para uma melhor tomada de decisão.
    - Criticar suas próprias respostas usando um prompt de feedback estruturado.
    - Refinar seus resultados de forma iterativa, seguindo regras predefinidas.
    - **************************************************************************
    TASKS:
    - Armazenar o histórico de conversa - Implementar um mecanismo de memória e
    traquear as interações anteriores.
    - Gerar uma resposta inicial - Processar a entrada do usuário e retornar a
    resposta usando o modelo de linguagem.
    - Criticar suas próprias respostas - Se a auto-reflexão estiver ativada, o
    agente deve gerar um feedback sobre a sua própria resposta.
    - Refinar suas respostas iterativamente - Baseada na auto-reflexão, o agente
    deve ajustar sua resposta para melhorar a clareza, acurária e relevância.

    STEPS:
    1. Criar uma camada de memória para armazenar o histórico de conversa.
    2. Introduzir um mecanismo de auto-reflexão que permita o agente analisar
    suas respostas e refina-las.
    3. Limitar o número de auto-reflexões, para prevenir loops excessivos (
        minimum_reflections = 1, maximum_reflections = 3
    )
    4. Garantir flexibilidade para o usuário ativar/desativar a auto-reflexão.

    CONSIDERATIONS:
    - O agente deve sempre gerar uma resposta inicial, antes de auto-reflexão..
    - Se auto-reflexão estiver ativada, deverá ser executada uma vez mais, para
    criticar e refinar a sua resposta.
    - O número de iterações deve ser controlado e não exceder o máximo de 3 refi-
    namentos.
    - Implementar uma funcionalidade de logging (verbose mode) para traquear o
    o processo de refinamento.

Classes já existentes:
    - ApiKeyLoader
    - OpenAIClient
    - Agent
    - Memory - adicionando um novo método: last_message()

'''

import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion


class ApiKeyLoader:
    """
    Carrega a chave da OpenAI (LLM) a partir de um arquivo .env.

    Args:
        env_path (Path): Caminho para o arquivo .env contendo a variável OPENAI_API_KEY.

    Example:
        >>> loader = ApiKeyLoader(Path(".env"))
        >>> api_key = loader.get_openai_key()
    """

    def __init__(self, env_path: Path):
        self.env_path = env_path

    def get_openai_key(self) -> str:
        """
        Carrega a chave da OpenAI do arquivo .env.

        Returns:
            str: A chave da API da OpenAI.

        Raises:
            ValueError: Se a variável OPENAI_API_KEY não estiver definida no .env.
        """
        load_dotenv(self.env_path)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        return api_key


class OpenAIClient:
    """
    Interface para interagir com a API da OpenAI.

    Esta é uma CAMADA DE ABSTRAÇÃO que:
    - Encapsula a configuração
    - Fornece uma interface simplificada
    - Pode adicionar funcionalidades extras

    Args:
        api_key (str): Chave da API da OpenAI. (fornecida externamente)

    Example:
        >>> client = OpenAIClient("sua-chave")
        >>> openai_client = client.get_client()
    """

    def __init__(self, api_key: str) -> None:
        """
        #* NÃO cria o cliente ainda - apenas armazena a configuração.
        Inicializa o cliente OpenAI.

        Args:
            api_key (str): Chave da API da OpenAI.
        """
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.api_key = api_key  # ✅ Armazena a chave recebida
        self._client: OpenAI | None = None  # ✅ Cliente será criado depois

    @property
    def client(self) -> OpenAI:
        """
        Lazy-load OpenAI client com cache.

        Returns:
            OpenAI: Instância configurada do cliente OpenAI e
            pronta para uso.
        """
        if self._client is None:  # * ← Primeira vez?
            self._client = self._create_client()  # * ← Cria o cliente
        return self._client  # * ← Retorna o cliente

    def get_client(self) -> OpenAI:
        """
        Retorna o objeto cliente OpenAI.

        Returns:
            OpenAI: Instância do cliente OpenAI.
        """
        return self.client

    def _create_client(self) -> OpenAI:
        """
        Método privado para criação do cliente.
        Facilita testes e extensibilidade.
        """
        return OpenAI(api_key=self.api_key)

    def __repr__(self) -> str:
        """Representação para debug."""
        return f"OpenAIClient(api_key='***{self.api_key[-4:]}')"


class Agent:
    """
    Agente para interagir com modelos de linguagem da OpenAI.

    Args:
        client (OpenAI): Instância do cliente OpenAI.
        name (str, opcional): Nome do agente. Padrão "AI Agent".
        role (str, opcional): Papel do agente. Padrão "You are a helpful
        assistant.".
        instructions (str, opcional): Instruções adicionais. Padrão
        "help the users with any question".
        model (str, opcional): Nome do modelo. Padrão "gpt-4.1".
        temperature (float, opcional): Temperatura da geração. Padrão 0.0.

    Example:
        >>> agent = Agent(client)
        >>> resposta = agent.invoke("Diga olá!")
    """

    def __init__(
        self,
        client: OpenAI,
        name: str = "AI Agent",
        role: str = "You are a helpful assistant.",
        instructions: str = "help the users with any question",
        model: str = "gpt-4.1",
        temperature: float = 0.0,
    ):
        self.client = client
        self.name = name
        self.role = role
        self.instructions = instructions
        self.model = model
        self.temperature = temperature

    def invoke(self, message: str) -> str:
        """
        Envia uma mensagem ao modelo de linguagem e retorna a resposta.

        Args:
            message (str): Mensagem do usuário para o agente.

        Returns:
            str: Resposta gerada pelo modelo.
        """
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": f"{self.role} {self.instructions}"},
            {"role": "user", "content": message},
        ]
        response: ChatCompletion = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=self.temperature
        )
        result: str = response.choices[0].message.content or ""
        return result


class Memory:
    """
    Classe simples para armazenar o histórico de mensagens de uma conversa.

    Cada mensagem é um dicionário com as chaves 'role' (papel: 'system',
    'user' ou 'assistant') e 'content' (conteúdo da mensagem).

    Exemplos de uso:
        >>> memory = Memory()
        >>> memory.add_message('system', 'Instrução para o agente.')
        >>> memory.add_message('user', 'O que é uma API?')
        >>> memory.add_message('assistant', 'Uma API é ...')
        >>> historico = memory.get_messages()
    """
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        """
        Adiciona uma nova mensagem ao histórico.

        Args:
            role (str): O papel da mensagem ('system', 'user' ou 'assistant').
            content (str): O texto da mensagem.
        """
        self.messages.append({"role": role, "content": content})

    def get_messages(self):
        """
        Retorna a lista de mensagens armazenadas.

        Returns:
            list: Lista de dicionários com as mensagens da conversa.
        """
        return self.messages

    def last_message(self):
        """
        Retorna a última mensagem armazenada.

        Returns:
            dict: Último dicionário com a mensagem da conversa.
        """
        return self.messages[-1]

class EnhancedAgent(Agent):
    """
    Agente de IA aprimorado com memória e auto-reflexão.
    
    Features implementadas:
    - Memória: Armazena histórico de conversas para melhor contexto
    - Auto-reflexão: Critica e refina suas próprias respostas
    - Logging: Rastreia o processo de geração e refinamento
    - Controle de iterações: Limita o número de auto-reflexões
    
    Args:
        client (OpenAI): Cliente OpenAI configurado
        name (str): Nome do agente
        role (str): Papel/função do agente
        instructions (str): Instruções específicas para o agente
        model (str): Modelo de linguagem a ser usado
        temperature (float): Temperatura para geração de respostas
        verbose (bool): Ativa logging detalhado
        reflection (bool): Ativa auto-reflexão por padrão
        max_iter (int): Número máximo de iterações de auto-reflexão
    """
    
    # Constante para o prompt de auto-crítica
    SELF_CRITIQUE_PROMPT = (
        "Leia a resposta abaixo, identifique possíveis erros, pontos de "
        "melhoria ou falta de clareza. "
        "Em seguida, forneça uma versão revisada e aprimorada da resposta, "
        "corrigindo os problemas encontrados.\n\n"
        "RESPOSTA ORIGINAL:\n{response}\n\n"
        "Sua crítica e versão revisada:"
    )
    
    def __init__(
        self,
        client: OpenAI,
        name: str = "AI Agent",
        role: str = "You are a helpful assistant.",
        instructions: str = "help the users with any question",
        model: str = "gpt-4.1",
        temperature: float = 0.0,
        verbose: bool = False,
        reflection: bool = False,
        max_iter: int = 1
    ):
        super().__init__(client, name, role, instructions, model, temperature)
        self.memory = Memory()
        self.verbose = verbose
        self.reflection = reflection
        self.max_iter = max_iter

    def invoke(self,
               message: str,
               auto_reflection: bool | None = None,
               max_reflections: int | None = None
               ) -> str:
        """
        Processa uma mensagem do usuário e retorna uma resposta.
        
        O método sempre gera uma resposta inicial primeiro. Se auto-reflexão
        estiver ativada, executa um processo iterativo de crítica e refinamento.
        
        Args:
            message (str): Mensagem do usuário
            auto_reflection (bool, opcional): Força ativação/desativação da
            auto-reflexão.
                                            Se None, usa o valor padrão da
                                            classe.
            max_reflections (int, opcional): Número máximo de iterações de
            auto-reflexão.Se None, usa o valor padrão da classe.
        
        Returns:
            str: Resposta final do agente (inicial ou refinada)
        """
        # Usa valores padrão da classe se não especificados
        auto_reflection = self.reflection if auto_reflection is None else auto_reflection
        max_reflections = self.max_iter if max_reflections is None else max_reflections
        
        # 1. SEMPRE gerar resposta inicial primeiro
        if self.verbose:
            logger.info(f"User message: {message}")
        self.memory.add_message("user", message)
        response = super().invoke(message)
        if self.verbose:
            logger.info(f"Initial assistant response: {response}")
        self.memory.add_message("assistant", response)

        # 2. Auto-reflexão (se ativada)
        if auto_reflection:
            if self.verbose:
                logger.info(f"Starting auto-reflection process (max {max_reflections} iterations)")
            
            for i in range(max_reflections):
                # Gera prompt de crítica com a resposta atual
                critique_prompt = self.SELF_CRITIQUE_PROMPT.format(response=response)
                
                if self.verbose:
                    logger.info(f"Self-critique iteration {i+1}/{max_reflections}")
                
                # Chama o modelo para crítica e refinamento
                critique_and_revision = super().invoke(critique_prompt)
                
                # Atualiza a resposta com a versão refinada
                response = critique_and_revision
                self.memory.add_message("assistant", response)
                
                if self.verbose:
                    logger.info(f"Revised response (iteration {i+1}): {response[:100]}...")

        # 3. Logging final e retorno
        if self.verbose:
            logger.debug(f"Final history: {len(self.memory.get_messages())} messages")
        
        return response


if __name__ == "__main__":
    #! Testando a camada de memória (Memory a abstração de uma lista de msgs)
    memory = Memory()
    memory.add_message("system", "You are a Python tutor.")
    memory.add_message("user", "What is a dictionary in Python?")
    memory.add_message("assistant", "A dictionary is a collection of key-value pairs.")
    print(memory.get_messages())
    print(memory.last_message())
    print("--------------------------------")
    
    #! Testando a implementação do EnhancedAgent
    #! Memory layer - Tarefa 1
    
    # * 1. Carregar a chave da OpenAI a partir do arquivo .env
    env_path = Path(__file__).resolve().parent / ".env"
    api_loader = ApiKeyLoader(env_path)
    openai_key = api_loader.get_openai_key()

    # * 2. Criar um client OpenAI
    openai_client = OpenAIClient(openai_key)
    client = openai_client.get_client()
    memory_agent = EnhancedAgent(client, verbose=True)
    print(memory_agent.invoke("Pick only one. Who is the best character in Game of Thrones?"))
    historico = memory_agent.memory.get_messages()
    print(historico)
    
    #* 3 - Testes de implementação
    ai_agent_enhanced = EnhancedAgent(
        client,
        verbose=True,
        reflection = True,
        max_iter=3)
    ai_agent_enhanced.memory.get_messages()
