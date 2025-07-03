ai_agent_prototype/
│
├── agent/                # Lógica principal do agente
│   ├── __init__.py
│   ├── agent.py          # Classe Agent
│   └── base.py           # (Opcional) Classes base/abstratas
│
├── tools/                # Ferramentas externas (funções, APIs, etc)
│   ├── __init__.py
│   ├── tool.py           # Classe Tool (abstração)
│   └── power.py          # Exemplo de ferramenta (ex: exponenciação)
│
├── memory/               # Gerenciamento de memória/conversa
│   ├── __init__.py
│   └── memory.py         # Classe Memory
│
├── llm_client/           # Cliente para LLMs (OpenAI, etc)
│   ├── __init__.py
│   └── openai_client.py  # Classe de integração com OpenAI
│
├── orchestrator/         # Orquestrador do fluxo (opcional)
│   ├── __init__.py
│   └── main.py           # Script principal de execução
│
├── tests/                # Testes unitários e de integração
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_tool.py
│   └── test_memory.py
│
├── docs/                 # Documentação do projeto
│   └── architecture.md
│
├── .env.example          # Exemplo de variáveis de ambiente
├── requirements.txt      # Dependências do projeto
├── README.md             # Documentação principal
└── pyproject.toml        # (Opcional) Configuração de build/poetry