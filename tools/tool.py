# tools\tool.py
"""Abstração para facilitar o uso de funções como ferramentas para um agente de IA.

Este módulo fornece a classe `Tool`, que envolve uma função Python e extrai
automaticamente metadados (como nome, descrição e parâmetros) para gerar um
esquema JSON compatível com a API de "function calling" de modelos como o da OpenAI.
"""

from collections.abc import Callable
from inspect import Parameter, signature
from typing import Any


class Tool:
    """Encapsula uma função para ser usada como uma ferramenta por um agente de IA.

    A classe realiza a introspecção de uma função Python para extrair seu nome,
    docstring (usado como descrição) e a assinatura dos seus parâmetros (nome,
    tipo e se é obrigatório).

    Com base nesses dados, ela pode gerar uma representação em formato JSON Schema,
    adequada para ser fornecida a modelos de linguagem para "function calling".

    Attributes:
        func (Callable): A função original que está sendo encapsulada.
        name (str): O nome da função.
        description (str): A descrição da ferramenta, extraída da primeira linha
            do docstring da função.
        parameters (list[dict]): Uma lista de dicionários, cada um descrevendo
            um parâmetro da função.
        required_params (list[str]): Uma lista com os nomes dos parâmetros que
            são obrigatórios.
    """

    # Definir os tipos dos atributos da classe
    func: Callable[..., Any]
    name: str
    description: str
    parameters: list[dict[str, Any]]
    required_params: list[str]

    def __init__(self, func: Callable[..., Any]) -> None:
        """Inicializa a ferramenta a partir de uma função.

        Args:
            func (Callable): A função a ser encapsulada. A função deve ter um
                docstring e anotações de tipo (type hints) para todos os seus
                parâmetros.

        Raises:
            TypeError: Se o objeto fornecido em `func` não for uma função chamável.
            ValueError: Se a função não possuir um docstring ou se algum de seus
                parâmetros não tiver uma anotação de tipo.
        """
        if not callable(func):
            msg = "Tool 'func' must be a callable function."
            raise TypeError(msg)
        if not func.__doc__:
            msg = (
                f"Function '{func.__name__}' must have a docstring "
                f"for its description."
            )
            raise ValueError(msg)

        self.func = func
        self.name = func.__name__
        self.description = func.__doc__.strip().split("\n")[0]

        sig = signature(self.func)
        self.parameters = []
        self.required_params = []

        for param in sig.parameters.values():
            # Ignora *args e **kwargs para simplificar
            if param.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
                continue

            # Valida se o parâmetro possui anotação de tipo
            if param.annotation is Parameter.empty:
                msg = (
                    f"Parameter '{param.name}' in function '{self.name}' "
                    f"is missing a type hint."
                )
                raise ValueError(msg)

            self.parameters.append({
                "name": param.name,
                "type": param.annotation,  # Armazena o tipo Python
                "description": "",  # Descrição extraída do docstring no futuro
            })

            # Verifica se o parâmetro é obrigatório
            if param.default is Parameter.empty:
                self.required_params.append(param.name)

    def __call__(self, *args: object, **kwargs: object) -> object:
        """Torna a instância da classe chamável, executando a função original.

        Args:
            *args: Argumentos posicionais a serem passados para a função
                encapsulada.
            **kwargs: Argumentos nomeados a serem passados para a função
                encapsulada.

        Returns:
            O resultado da execução da função original.
        """
        return self.func(*args, **kwargs)

    def _map_type_to_json_schema(self, py_type: type) -> str:
        """Mapeia um tipo Python para o tipo correspondente no JSON Schema.

        Args:
            py_type (type): O tipo Python a ser mapeado (ex: str, int, bool).

        Returns:
            str: O nome do tipo correspondente no JSON Schema
                (ex: "string", "integer").
        """
        if py_type is str:
            return "string"
        if py_type is int:
            return "integer"
        if py_type is float:
            return "number"
        if py_type is bool:
            return "boolean"
        # Para outros tipos, o padrão é "string", mas pode ser expandido.
        return "string"

    def to_dict(self) -> dict[str, Any]:
        """Gera a representação da ferramenta em formato de dicionário.

        Este formato é compatível com a especificação de "function calling"
        da API da OpenAI.

        Returns:
            dict: Um dicionário representando a ferramenta no formato JSON Schema.
        """
        properties = {}
        for param in self.parameters:
            properties[param["name"]] = {
                "type": self._map_type_to_json_schema(param["type"]),
                "description": param.get("description", "")
            }

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": self.required_params,
                },
            },
        }

    def to_openai_spec(self) -> dict[str, Any]:
        """Retorna o dicionário no formato esperado pela API OpenAI."""
        return self.to_dict()


if __name__ == "__main__":
    import json

    from . import power  # type: ignore

    print("--- Demonstração da classe Tool com a função 'power' ---")

    try:
        #* 1. Instanciamos a classe Tool com a nossa função 'power'.
        #* A classe irá inspecionar a função e extrair seus metadados.
        power_tool = Tool(power)
        print("\n[PASSO 1] Instância da Tool criada com sucesso!")

        #* 2. Exibimos os atributos que a classe extraiu da função.
        print("\n[PASSO 2] Atributos extraídos da função:")
        print(f"  - Nome: {power_tool.name}")
        print(f"  - Descrição: {power_tool.description}")
        print(f"  - Parâmetros: {power_tool.parameters}")
        print(f"  - Parâmetros obrigatórios: {power_tool.required_params}")

        #* 3. Geramos o dicionário no formato JSON Schema, pronto para a API.
        tool_schema = power_tool.to_dict()
        print("\n[PASSO 3] Dicionário gerado pelo método .dict():")
        #* Usamos json.dumps para uma impressão mais legível (pretty-print)
        print(json.dumps(tool_schema, indent=2, ensure_ascii=False))

        #* 4. Usamos a instância da Tool como se fosse a função original.
        #* A classe implementa __call__, então podemos chamá-la diretamente.
        BASE = 3
        EXPOENTE = 4
        resultado = power_tool(base=BASE, exponent=EXPOENTE)
        print("\n[PASSO 4] Executando a ferramenta diretamente:")
        print(f"  - Chamando: {power_tool.name}(base={BASE}, exponent={EXPOENTE})")
        print(f"  - Resultado: {resultado}")

    except (TypeError, ValueError) as e:
        print(f"\nOcorreu um erro durante a demonstração: {e}")
