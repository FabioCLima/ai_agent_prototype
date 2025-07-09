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

   ```bash
   pip install -r requirements.txt
   ```

2. Configure sua chave de API no arquivo `.env` (veja `.env.example`).
3. Execute o orquestrador:

   ```bash
   python main.py
   ```

## Status do Projeto Detalhado

### Agent

- [x] Classe principal do agente
- [x] Integração com memória e LLM
- [x] Registro e chamada de ferramentas
- [ ] Suporte completo a function calling sugerido pelo LLM
- [ ] Suporte a múltiplas tool calls em uma mesma interação

### Tools

- [x] Classe abstrata `Tool`
- [x] Exemplo de ferramenta implementada (`power.py`)
- [ ] Adicionar mais ferramentas de exemplo
- [ ] Melhorar tratamento de erros nas ferramentas

### Memory

- [x] Classe para gestão do histórico de mensagens
- [ ] Testes unitários e documentação detalhada

### LLM Client

- [x] Integração básica com OpenAI GPT
- [ ] Suporte a outros provedores (opcional)
- [ ] Melhorar logging e tratamento de erros

### Testes

- [ ] Testes unitários para todos os módulos
- [ ] Testes de integração do fluxo completo

### Documentação

- [x] Documentação básica do projeto
- [ ] Docstrings e exemplos em todas as classes/funções
- [ ] Atualizar docs conforme novas features

### Interface

- [x] Orquestrador simples via linha de comando (`main.py`)
- [ ] Interface CLI aprimorada ou interface web (opcional)

## Exemplos de Uso

### Execução Básica

```bash
python main.py
```

### Exemplo de Interação Simples

Usuário:

```
Qual a capital da França?
```

Resposta do agente:
```
A capital da França é Paris.
```

### Exemplo de Uso de Ferramenta (Tool Call)

Usuário:
```
Calcule 2 elevado a 8 usando a ferramenta.
```
Resposta do agente:
```
Utilizando a ferramenta de exponenciação:
2 ^ 8 = 256
```

> O agente identifica a necessidade de usar a ferramenta `power` e executa a operação, retornando o resultado ao usuário.

## Roadmap

Veja o arquivo `docs/architecture.md` para detalhes de arquitetura e próximos passos.
