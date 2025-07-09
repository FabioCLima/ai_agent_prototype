# project: ai-agent-prototype
# author: Fabio Lima
# date: 09/07/2025
# description: main file for ai-agent-prototype
'''
AI Agent Prototype - Entry point for the AI Agent Prototype project
'''
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from agent.agent_ai import AgentAI
from llm_client.openai_client import ApiKeyLoader, OpenAIClient
from tools.power import power
from tools.tool import Tool


def main():
    print("Teste passo a passo do agente com tools e memória\n")

    # 1. Criar agente com tool power
    agent = AgentAI(llm_client=OpenAIClient(ApiKeyLoader(Path(".env")).get_openai_key()),
                    tools=[Tool(power)])
    print("Agente criado com tool 'power'.")
    print("Memória inicial:", agent.memory.messages, "\n")

    # 2. agent.invoke("What is 10 + 5?")
    resposta1 = agent.invoke("What is 10 + 5?")
    print("Resposta 1:", resposta1)
    print("Memória após pergunta 1:", agent.memory.messages, "\n")

    # 3. Inspecionar memória
    print("Memória atual:", agent.memory.messages, "\n")

    # 4. Resetar memória
    agent.memory.reset()
    print("Memória após reset:", agent.memory.messages, "\n")

    # 5. Perguntar potência
    resposta2 = agent.invoke("What is 2 to the power of 8?")
    print("Resposta 2:", resposta2)
    print("Memória após pergunta 2:", agent.memory.messages, "\n")

    # 6. Inspecionar memória
    print("Memória atual:", agent.memory.messages, "\n")

    # 7. Pergunta composta
    resposta3 = agent.invoke("What is 3 to the power of (2 to the power of 2)?")
    print("Resposta 3:", resposta3)
    print("Memória após pergunta 3:", agent.memory.messages, "\n")

    # 8. Inspecionar memória final
    print("Memória final:", agent.memory.messages)

if __name__ == "__main__":
    main()
