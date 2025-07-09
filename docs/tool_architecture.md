# Tool Architecture Plan

___

## Introduction

This document outlines the architecture plan for the tool. It provides an overview of the tool's components, their interactions, and the overall structure of the tool.
Is designed to wrap a function and provide a way to automatically generate a JSON schema on the functions's type hints and signature.

### Key tasks include

    1. Extracting function name and description from dunder (__name__, __doc__) properties.
    2. Parsing type hints and parameters signature.
    3. Inferring JSON schema types (e.g., float -> number, int -> integer, etc.)

### Key Components

    1. Construtor: The __init__ method takes a function (`external == func`) as an argument (`Callable`)
    and extracts its name, description, and parameters.
    2. Infer JSON Schema Type: The `infer_json_schema_type` method uses the function's type hints and signature to generate a JSON schemma maps Python types such: 
    (float, int, ...) to JSON schema types (number, integer, ...).
    3. Calling the Function: The `call` method allows invoke the wrapped function with keyword arguments.

    import json
    from inspect import signature, getdoc, get_type_hints

    class Tool:
        def __init__(self, func):
            self.func = func
            self.name = func.__name__
            self.description = getdoc(func) or "No description available."
            self.parameters = self._generate_parameters()

        def _generate_parameters(self):
            params = {}
            hints = get_type_hints(self.func)
            sig = signature(self.func)

            for param in sig.parameters.values():
                param_type = self.infer_json_schema_type(hints[param.name])
                params[param.name] = {
                    "type": param_type,
                    "required": param.default is param.empty
                }
            
            return {
                "type": "object",
                "properties": params,
                "required": [name for name, details in params.items() if details["required"]]
            }

        def infer_json_schema_type(self, arg_type):
            if arg_type is bool:
                return "boolean"
            elif arg_type is int:
                return "integer"
            elif arg_type is float:
                return "number"
            elif arg_type is str:
                return "string"
            elif arg_type is list:
                return "array"
            elif arg_type is dict:
                return "object"
            else:
                return "string"  # Fallback for unsupported types

        def call(self, **kwargs):
            return self.func(**kwargs)

___
