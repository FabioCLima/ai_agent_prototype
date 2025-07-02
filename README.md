# AI Agent Prototype

Este projeto é um protótipo modular de um Agente de IA capaz de decidir quando usar ferramentas externas (function calling), mantendo contexto conversacional e integrando-se a LLMs como OpenAI GPT.

## Estrutura

- `agent/` — Lógica do agente e orquestração de decisões
- `tools/` — Ferramentas externas disponíveis para o agente
- `memory/` — Gerenciamento do histórico da conversa
- `llm_client/` — Integração com modelos de linguagem
- `tests/` — Testes unitários
- `docs/` — Documentação detalhada

## Como rodar

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
2. Configure sua chave de API no arquivo `.env` (veja `.env.example`).
3. Execute o orquestrador:
   ```
   python orchestrator/main.py
   ```

## Roadmap

Veja o arquivo `docs/architecture.md` para detalhes de arquitetura e próximos passos.
