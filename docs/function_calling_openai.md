# Guia Completo: Function Calling com OpenAI

## O que é Function Calling?

**Function Calling** é a capacidade de um modelo de linguagem (como GPT) fazer chamadas para funções externas durante uma conversa. É importante entender que o modelo **não executa** as funções - ele apenas solicita que você as execute.

## Fluxo de Execução do Function Calling

### **Etapa 1: Preparação**

- Você define um **JSON schema** que descreve sua função externa
- Este schema informa ao modelo: nome da função, o que ela faz, quais parâmetros aceita
- Você envia uma mensagem do usuário + o JSON schema para a OpenAI

### **Etapa 2: Análise do Modelo**

- O modelo GPT lê a mensagem do usuário
- Ele analisa se precisa usar alguma função externa para responder
- **Decisão**: "Preciso calcular uma potência? Então vou usar a função power!"

### **Etapa 3: Solicitação de Função**

- O modelo **NÃO executa** a função (ele não tem acesso a ela)
- Em vez disso, ele retorna uma "solicitação": "Por favor, execute a função power com base=2 e exponent=3"
- Esta solicitação vem no formato `tool_calls`

### **Etapa 4: Execução Local**

- **Você** (seu código) recebe esta solicitação
- **Você** executa a função externa real (power) no seu ambiente
- **Você** obtém o resultado (exemplo: 8)

### **Etapa 5: Retorno do Resultado**

- **Você** envia o resultado de volta para o modelo
- Formato: "A função power retornou: 8"
- Isso é adicionado à conversa como uma mensagem de "tool"

### **Etapa 6: Resposta Final**

- O modelo recebe o resultado da função
- Agora ele pode formular uma resposta completa para o usuário
- Exemplo: "O resultado de 2 elevado a 3 é 8"

## Resumo do Fluxo

```mermaid
Usuário: "Quanto é 2³?"
    ↓
Modelo: "Preciso usar a função power(2, 3)"
    ↓
Seu código: Executa power(2, 3) = 8
    ↓
Modelo: "O resultado de 2³ é 8"
    ↓
Usuário recebe a resposta final
```

## Pontos Importantes

- **O modelo nunca executa as funções** - ele apenas solicita
- **Você sempre executa** as funções no seu ambiente
- **É um ping-pong**: Usuário → Modelo → Sua função → Modelo → Usuário
- **O JSON schema é como um "manual"** que ensina o modelo sobre suas funções
- **Cada função externa precisa do seu próprio JSON schema**

## Pergunta Comum: E se eu quiser usar APIs externas?

**Resposta:** Sim, você precisa ter a função definida localmente, MAS a função local pode ser apenas um "wrapper" que chama APIs externas!

### Exemplo Prático: Previsão do Tempo

**Cenário:** Usuário pergunta: "Qual é a previsão de temperatura para Petrópolis amanhã, dia 05/07/2025?"

#### Etapa 1: Definir o JSON Schema

```json
{
    "name": "get_weather_forecast",
    "description": "Obtém a previsão do tempo para uma cidade específica",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Nome da cidade"
            },
            "date": {
                "type": "string",
                "description": "Data no formato DD/MM/YYYY"
            }
        },
        "required": ["city", "date"]
    }
}
```

#### Etapa 2: Implementar a Função Local

```python
import requests

def get_weather_forecast(city: str, date: str) -> str:
    """
    Função local que faz chamada para API externa de clima
    """
    # Chama API do OpenWeatherMap, WeatherAPI, etc.
    response = requests.get(f"https://api.weather.com/forecast?city={city}&date={date}")
    weather_data = response.json()
    return f"Temperatura em {city} no dia {date}: {weather_data['temperature']}°C"
```

#### Fluxo Completo do Exemplo

1. **Modelo analisa:** "Preciso de dados meteorológicos externos"
2. **Modelo solicita:** "Execute get_weather_forecast(city='Petrópolis', date='05/07/2025')"
3. **Sua função local:**
   - Recebe os parâmetros
   - Faz chamada HTTP para API de clima
   - Processa a resposta da API
   - Retorna dados formatados
4. **Resultado volta para o modelo:** "Temperatura em Petrópolis no dia 05/07/2025: 22°C"
5. **Modelo responde ao usuário:** "A previsão para Petrópolis amanhã é de 22°C"

## Tipos de "Funções Externas" Possíveis

### APIs REST

- Previsão do tempo
- Cotação de moedas
- Notícias
- Dados de estoque

### Bancos de Dados

- Consultas SQL
- Busca em documentos
- Histórico de conversas

### Serviços Cloud

- AWS, Google Cloud, Azure
- Processamento de imagens
- Análise de documentos

### Sistemas Internos

- ERP da empresa
- CRM
- Sistemas de inventário

## Conceito Chave

A **função local** é apenas um **"tradutor"** entre:

- O que o modelo quer (formato padronizado)
- O que o serviço externo oferece (API específica)

## Exemplo de Agente Completo

Um agente de IA pode ter múltiplas ferramentas:

```python
tools = [
    {"name": "get_weather", ...},           # API de clima
    {"name": "get_stock_price", ...},       # API financeira  
    {"name": "search_database", ...},       # Banco de dados local
    {"name": "send_email", ...},            # Serviço de email
    {"name": "calculate_power", ...}        # Função matemática pura
]
```

## Resumo para Agentes de IA

**Function Calling** é a base para criar agentes inteligentes que podem:

- Interagir com o mundo real
- Acessar dados externos
- Executar tarefas específicas
- Integrar múltiplos serviços

O modelo de linguagem atua como o "cérebro" que decide quando e como usar cada ferramenta, enquanto você fornece as ferramentas reais.
