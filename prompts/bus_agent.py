from langchain.prompts import ChatPromptTemplate

bus_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an assistant that provides bus information. You are not allowed to ask user questions.""",
        ),
        ("placeholder", "{chat_history}"),
        ("user", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
        ("system","Remember, You are not allowed to ask user questions.")
    ]
)
