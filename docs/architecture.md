# Arquitetura do Agente de IA

## Componentes

- **Agent**: Orquestra o fluxo, decide quando usar ferramentas, integra memória e LLM.
- **Tool**: Abstração para funções externas (ex: cálculos, APIs).
- **Memory**: Gerencia o histórico da conversa.
- **LLM Client**: Interface para modelos de linguagem (OpenAI, etc).

## Fluxo de execução

1. Usuário envia mensagem.
2. Agent atualiza a memória.
3. Agent consulta o LLM, informando ferramentas disponíveis.
4. LLM responde (diretamente ou solicitando uso de ferramenta).
5. Agent executa ferramenta, atualiza memória e retorna ao LLM se necessário.
6. Agent responde ao usuário.

## Princípios

- Modularidade
- Encapsulamento
- Testabilidade
- Documentação clara
