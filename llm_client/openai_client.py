#* Project: AI Agent Prototype
#ai_agent_prototype/llm_client/openai_client.py
# Description: This module loads the OpenAI API key from a file and creates a client
# object for the OpenAI API.

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


#! Class: ApiKeyLoader: Loads the OpenAI API key from a .env file
class ApiKeyLoader:
    """
    A utility class to load the OpenAI API key from a specified .env file.

    Args:
        env_path (Path): Path to the .env file containing the OPENAI_API_KEY variable.

    Example:
        >>> loader = ApiKeyLoader(Path(".env"))
        >>> try:
        ...     api_key = loader.get_openai_key()
        ... except ValueError as e:
        ...     print(f"Failed to load API key: {e}")
    """

    def __init__(self, env_path: Path):
        """
        Initializes the ApiKeyLoader with the path to the .env file.

        Args:
            env_path (Path): Path to the .env file.

        Raises:
            ValueError: If the provided path does not exist or is not a file.
        """
        if not env_path.exists():
            raise ValueError(f"Invalid path: '{env_path}' does not exist.")
        if not env_path.is_file():
            raise ValueError(f"'{env_path}' is not a valid file.")

        self.env_path = env_path

    def get_openai_key(self) -> str:
        """
        Loads and returns the OpenAI API key from the .env file.

        Returns:
            str: The OpenAI API key.

        Raises:
            ValueError: If OPENAI_API_KEY is missing or empty in the .env file.
        """
        load_dotenv(self.env_path)
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in the .env file.")
        return api_key


#! Class: OpenAIClient: A high-level abstraction for the OpenAI API client
class OpenAIClient:
    """
    A high-level abstraction layer for interacting with the OpenAI API.

    This class:
    - Encapsulates client configuration
    - Provides a simplified interface
    - Supports lazy initialization and caching
    - Enables easy testing/extensibility

    Args:
        api_key (str): OpenAI API key (must be provided externally).

    Example:
        >>> client = OpenAIClient("your-api-key")
        >>> openai_client = client.client  # Lazy-loaded property
        >>> # Or:
        >>> openai_client = client.get_client()  # Explicit method
    """

    def __init__(self, api_key: str) -> None:
        """
        Initializes the OpenAI client configuration (does not create the client yet).

        Args:
            api_key (str): Valid OpenAI API key.

        Raises:
            ValueError: If api_key is empty or None.
        """
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.api_key = api_key
        self._client: OpenAI | None = None  #* Lazy-loaded client

    @property
    def client(self) -> OpenAI:
        """
        Provides lazy-loaded, cached access to the OpenAI client instance.

        Returns:
            OpenAI: Configured and ready-to-use OpenAI client.

        Note:
            The client is created on first access (singleton pattern).
        """
        if self._client is None:  #* first access, creates the client
            self._client = self._create_client()
        return self._client

    def get_client(self) -> OpenAI:
        """
        Alternative access method for the OpenAI client (explicit version).

        Returns:
            OpenAI: Configured OpenAI client instance.
        """
        return self.client

    def _create_client(self) -> OpenAI:
        """
        Private method for client creation (separated for testability/extensibility).

        Returns:
            OpenAI: New OpenAI client instance.
        """
        return OpenAI(api_key=self.api_key)

    def __repr__(self) -> str:
        """
        Debug-friendly representation (masks sensitive API key).

        Returns:
            str: Safe string representation.
        """
        return f"OpenAIClient(api_key='***{self.api_key[-4:]}')"


if __name__ == "__main__":
    #* Example usage
    try:
        env_path: Path = Path(__file__).resolve().parent / ".env"
        loader:ApiKeyLoader = ApiKeyLoader(Path(env_path))
        api_key = loader.get_openai_key()
        print(f"Loaded OpenAI API key: {api_key}[:10]...") #* Masked output for security
        client = OpenAIClient(api_key)
        openai_client = client.client  #* Lazy-loaded property
        print(f"OpenAI client created: {openai_client}[:10]")
    except ValueError as e:
        print(f"Error: {e}")