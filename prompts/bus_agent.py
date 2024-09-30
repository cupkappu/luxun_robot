from langchain.prompts import ChatPromptTemplate

bus_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an assistant that provides bus information. Your tools include:
- get_kmb_route_list: Retrieve a list of available bus routes.
- get_route_info: Retrieve information about a specific bus route.
- get_stop_list: Retrieve a list of stops for a specific route.
- get_bus_stop_info: Retrieve information about a specific bus stop.
- get_eta_info: Retrieve estimated time of arrival (ETA) for buses.
- get_stop_eta_info: Retrieve ETA information for a specific stop.
- get_route_eta_info: Retrieve ETA information for a specific route.""",
        ),
        ("placeholder", "{chat_history}"),
        ("query", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)
