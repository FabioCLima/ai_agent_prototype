#!/usr/bin/python
# -*- coding: utf-8 -*-
# ai_agent_prototype/tools/power.py
'''
A module to define the Power function and its corresponding JSON schema.
This module defines the Power function, which is a tool that can be used by an AI agent
to perform various tasks.
'''
#! Power function definition
def power(base: float, exponent: float) -> float:
    """
    Calculate the power of a base number raised to an exponent.
    
    Args:
        base (float): The base number
        exponent (float): The exponent to raise the base to
        
    Returns:
        float: The result of base^exponent
        
    Raises:
        ValueError: If base is negative and exponent is fractional
        OverflowError: If the result is too large to represent
    """
    try:
        return base ** exponent
    except (ValueError, OverflowError) as e:
        raise e

tools = [
    {
        "name": "power",
        "description": "Calculate the power of a base number raised to an exponent.",
        "parameters": {
            "type": "object",
            "properties": {
                "base": {
                    "type": "number",
                    "description": "The base number"
                },
                "exponent": {
                    "type": "number",
                    "description": "The exponent to raise the base to"
                }
            },
            "required": ["base", "exponent"]
        }
    }
]

def chat_with_tools(user_message, tools, memory):
  memory.add_message("user", user_message)
  response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=memory.get_messages(),
      tools=tools
  )
  ai_message = response.choices[0].message
  memory.add_message("assistant", ai_message.content, tool_calls=ai_message.tool_calls)
  return ai_message

if __name__ == "__main__":
    import inspect
    from typing import get_type_hints

    print(f"Documentação da função power: {power.__doc__}\n")
    print(f"Assinatura da função power: {inspect.signature(power)}\n")
    print(f"Tipos de retorno da função power: {get_type_hints(power)}\n")
