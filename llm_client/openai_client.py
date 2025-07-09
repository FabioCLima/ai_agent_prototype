# * Project: AI Agent Prototype
# ai_agent_prototype/llm_client/openai_client.py
# Description: This module loads the OpenAI API key from a file and creates a client
# object for the OpenAI API.

'''A simple AI agent '''

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


class ApiKeyLoader:
    # * Loads the OpenAI API key from a .env file
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

    def __init__(self, env_path: Path) -> None:
        """
        Initializes the ApiKeyLoader with the path to the .env file.

        Args:
            env_path (Path): Path to the .env file.

        Raises:
            ValueError: If the provided path does not exist or is not a file.
        """
        if not env_path.exists():
            msg = f"Invalid path: '{env_path}' does not exist."
            raise ValueError(msg)
        if not env_path.is_file():
            msg = f"'{env_path}' is not a valid file."
            raise ValueError(msg)

        self.env_path: Path = env_path

    def get_openai_key(self) -> str:
        """
        Loads and returns the OpenAI API key from the .env file.

        Returns:
            str: The OpenAI API key.

        Raises:
            ValueError: If OPENAI_API_KEY is missing or empty in the .env file.
        """
        load_dotenv(self.env_path)
        api_key: str | None = os.getenv("OPENAI_API_KEY")

        if not api_key:
            msg = "The OPENAI_API_KEY environment variable is not set in the .env file."
            raise ValueError(msg)
        return api_key


class OpenAIClient:
    # A high-level abstraction for the OpenAI API client
    """
    A high-level abstraction layer for interacting with the OpenAI API.
    This class:
    - Encapsulates client configuration
    - Provides a simplified interface

    Args:
        api_key (str): OpenAI API key (must be provided externally)
        >>> client = OpenAIClient("your-api-key")
        >>> openai_client = client.client  # Lazy-loaded property
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
            msg = "OpenAI API key is required"
            raise ValueError(msg)
        self.api_key: str = api_key
        self._client: OpenAI | None = None  # Cache for the OpenAI client

    @property
    def client(self) -> OpenAI:
        """
        Provides lazy-loaded, cached access to the OpenAI client instance.

        Returns:
            OpenAI: Configured and ready-to-use OpenAI client.

        Note:
            The client is created on first access (singleton pattern).
        """
        if self._client is None:  # * first access, creates the client
            self._client = self._create_client()
        return self._client

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
    # * Example usage
    try:
        env_file_path: Path = Path(__file__).resolve().parent / ".env"
        loader: ApiKeyLoader = ApiKeyLoader(Path(env_file_path))
        openai_api_key = loader.get_openai_key()
        print(
            f"Loaded OpenAI API key: {openai_api_key}[:10]..."
        )  # * Masked output for security
        client = OpenAIClient(openai_api_key)
        openai_client = client.client  # * Lazy-loaded property
        print(f"OpenAI client created: {openai_client}[:10]")
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Error: {e}")
