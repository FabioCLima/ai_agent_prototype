class Agent:
    """A tool-calling AI Agent"""

    def __init__(
        self,
        name:str = "Agent", 
        role:str = "Personal Assistant",
        instructions:str = "Help users with any question",
        model:str = "gpt-4o-mini",
        temperature:float = 0.0,
        tools:List[Tool] = [],
    ):

        self.name = name
        self.role = role
        self.instructions = instructions
        self.model = model
        self.temperature = temperature
        self.memory = Memory()
        self.memory.add_message(
            role="system",
            content=f"You're an AI Agent, your role is {self.role}, " 
                    f"and you need to {self.instructions}",
        )

        self.client = OpenAI()

        self.tools = tools
        self.tool_map = {t.name:t for t in tools}
        self.openai_tools = [t.dict() for t in self.tools] if self.tools else None

    def invoke(self, user_message: str) -> str:
        self.memory.add_message(
            role="user",
            content=user_message,
        )

        ai_message = self._get_completion(
            messages = self.memory.get_messages(),
        )

        tool_calls = ai_message.tool_calls
        self.memory.add_message(
            role="assistant",
            content=ai_message.content,
            tool_calls=tool_calls,
        )

        if tool_calls:
            self._call_tools(tool_calls)
            
        return self.memory.last_message()

    def _call_tools(self, tool_calls:List[ChatCompletionMessageToolCall]):
        for t in tool_calls:
            tool_call_id = t.id
            function_name = t.function.name
            args = json.loads(t.function.arguments)
            callable_tool = self.tool_map[function_name]
            result = callable_tool(**args)
            self.memory.add_message(
                role="tool", 
                content=str(result), 
                tool_call_id=tool_call_id
            )

        ai_message = self._get_completion(
            messages = self.memory.get_messages(),
        )

        tool_calls = ai_message.tool_calls

        self.memory.add_message(
            role="assistant",
            content=ai_message.content,
            tool_calls=tool_calls,
        )

        if tool_calls:
            self._call_tools(tool_calls)


    def _get_completion(self, messages:List[Dict])-> ChatCompletionMessage:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
            tools=self.openai_tools,
        )
        
        return response.choices[0].message