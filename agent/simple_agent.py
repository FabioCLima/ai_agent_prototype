#agent/agent.py
'''Um agente básico de IA. Sem memória, sem ferramentas.'''

from pathlib import Path

from openai import OpenAI

from llm_client.openai_client import ApiKeyLoader, OpenAIClient


class Agent:
    """
    A basic AI agent class for interacting with OpenAI's language models.
    
    Attributes:
        client (OpenAI): The OpenAI client used for generating responses.
        name (str, optional): Name of the agent. Defaults to "AI Agent".
        role (str, optional): System role description. Defaults to "You are a helpful
        assistant.".
        instructions (str, optional): Additional instructions for the agent. Defaults to
        "help the users with any question".
        model (str, optional): OpenAI model to use. Defaults to "gpt-4.1".
        temperature (float, optional): Sampling temperature for response generation.
        Defaults to 0.0.
    
    Methods:
        invoke(message: str) -> str: Generates a response to the given user message
        using the configured OpenAI client.
    """
    def __init__(
    self,
    client: OpenAI,
    name: str = "AI Agent",
    role: str = "You are a helpful assistant.",
    instructions: str = "help the users with any question",
    model: str = "gpt-4.1",
    temperature: float = 0.0
    ):
        self.client = client
        self.name = name
        self.role = role
        self.instructions = instructions
        self.model = model
        self.temperature = temperature

    def invoke(self, message: str) -> str:
        """
            Generates a response to a user message using the configured OpenAI client.
        
            Args:
                message (str): The user's input message to be processed.
        
            Returns:
                str: The generated response from the AI model, or an empty string if no
                response is generated.
        """
        messages = [
                {"role": "system", "content": f"{self.role} {self.instructions}"},
                {"role": "user", "content": message}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )
        result = response.choices[0].message.content or ""
        return result


if __name__ == "__main__":
    #* O caminho para o .env deve ser relativo à raiz do projeto.
    #* __file__ -> agent/agent.py
    #* .parent -> agent/
    #* .parent.parent -> raiz do projeto (ai_agent_prototype/)
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"
    loader: ApiKeyLoader = ApiKeyLoader(env_path)
    api_key = loader.get_openai_key()
    client_wrapper = OpenAIClient(api_key)
    openai_client = client_wrapper.client
    agent = Agent(openai_client)
    print(agent.invoke("What is the capital of France?"))
