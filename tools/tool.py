'''
Tool class - An abstraction to make it easier to build a tool.
Precisamos extrair todas as informações da função (func) para  construir o JSON Schema.
    1. func.__name__
    2. func.__doc__ (descrição da função)
    3  inspect.signature(func) - obter nomes, tipos e se são argumentos obrigatórios
'''

from inspect import Parameter, signature
from typing import Callable


class Tool:
    def __init__(self, func: Callable):
        #* 1. Validação inicial
        if not callable(func):
            raise TypeError("func must be a callable")
        if not func.__name__:
            error_msg = f"A função '{func.__name__}' tem que uma docstring com sua descrição"
            raise ValueError(f"{error_msg}")
        
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__.strip().split('\n')[0] #* pega a primeira linha
        
        #* 2. Instrospecção dos parâmetros da função
        #* fun_signature = inspect.signature(func)
        #* params = fun_signature.parameters
        sig = signature(self.func)
        self.parameters =[]
        self.required_params = []

        for param in sig.parameters.values():
            # Ignora *args e **kwargs por simplicidade
            if param.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
                continue

            # Valida se o parâmetro tem anotação de tipo
            if param.annotation is Parameter.empty:
                raise ValueError(f"Parameter '{param.name}' in function '{self.name}' is missing a type hint.")

            self.parameters.append({
                "name": param.name,
                "type": param.annotation, # Guardamos o tipo Python por enquanto
                "description": "" # Deixaremos a descrição do parâmetro para depois
            })

            # Verifica se o parâmetro é obrigatório
            if param.default is Parameter.empty:
                self.required_params.append(param.name)

    def _map_type_to_json_schema(self, py_type: type) -> str:
            """Mapeia tipos Python para tipos JSON Schema."""
        if py_type is str:
            return "string"
        if py_type is int:
            return "integer"
        if py_type is float:
            return "number"
        if py_type is bool:
            return "boolean"
        # Para outros tipos, o padrão é string, mas pode ser expandido
        return "string"

    def dict(self):
        """Retorna a representação da ferramenta em JSON Schema para a API OpenAI."""
        properties = {}
        for param in self.parameters:
            properties[param['name']] = {
                "type": self._map_type_to_json_schema(param['type']),
                "description": param.get('description', '') # Usa a descrição se houver
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

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)