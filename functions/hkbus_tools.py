from agents.percive_agent import percive_agent
from functions.qq import QQAgent
from typing import Annotated, List
from langchain.tools import tool
import requests
from prompts.bus_agent import bus_prompt
from langchain_core.language_models import BaseChatModel
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor

g_agent:percive_agent = None
qq_agents: List[QQAgent]
bus_agent = None

def give_callback(agent: percive_agent, **kwargs):
    global g_agent, qq_agents
    g_agent = agent
    qq_agents = kwargs.get('functions.qq',[])
    for i in qq_agents:
        i.agent.add_tools(bus_info_agent_factory(tool_factory(),llm=g_agent.llm))
        i.agent.augmented_prompts[''] = augmented_prompt

async def start_callback():
    pass

def bus_info_agent_factory(tools,llm: BaseChatModel):
    agent = create_react_agent(llm, tools, bus_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    @tool
    def ask_bus_info(query:  Annotated[str,"The query of bus information, could be route or stops or somethings."]):
        """Get the bus information, include stop and route and ETA info."""
        return agent_executor.invoke({"query": query})['output']
    return [ask_bus_info]

def tool_factory():
    @tool
    def get_kmb_route_list() -> dict:
        """
        Fetches the list of all bus routes of KMB.
        """

        base_url = "https://data.etabus.gov.hk/"
        endpoint = "v1/transport/kmb/route/"
        full_url = base_url + endpoint
        response = requests.get(full_url)
        return response.json()

    @tool
    def get_route_info(route: Annotated[str, "The route number of the respective bus company"], direction: Annotated[str, "The direction of the route"], service_type: Annotated[str, "The service type of the bus route"]) -> dict:
        """
        Fetches route information for a specified KMB bus route.
        """
        base_url = "https://data.etabus.gov.hk"
        endpoint = f"/v1/transport/kmb/route/{route}/{direction}/{service_type}"
        url = base_url + endpoint
        response = requests.get(url)
        return response.json()
    @tool
    def get_stop_list() -> dict:
        """
        Retrieves all bus stop information from the KMB Stop List API.
        """
        base_url = "https://data.etabus.gov.hk/"
        response = requests.get(f"{base_url}/v1/transport/kmb/stop")
        return response.json()

    @tool
    def get_bus_stop_info(stop_id: Annotated[str, "16-character representation of a bus stop"]) -> dict:
        """
        Fetches bus stop information for a given stop ID.
        """
        base_url = "https://data.etabus.gov.hk/"
        endpoint = "/v1/transport/kmb/stop/{stop_id}"
        url = base_url + endpoint.format(stop_id=stop_id)
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch data", "status_code": response.status_code}
    @tool
    def get_eta_info(stop_id: Annotated[str, "16-characters representation of a bus stop"], route: Annotated[str, "The route number of the respective bus company"], service_type: Annotated[str, "The service type of the bus route"]) -> dict:
        """
        Retrieves the ETA information for a specific stop ID, route, and service type.
        """
        base_url = "https://data.etabus.gov.hk/"
        endpoint = f"/v1/transport/kmb/eta/{stop_id}/{route}/{service_type}"
        url = base_url + endpoint
        response = requests.get(url)
        return response.json()

    @tool
    def get_stop_eta_info(stop_id: Annotated[str, "16-characters representation of a bus stop"]) -> dict:
        """
        Retrieves the ETA information for all routes at a specific stop.
        """
        base_url = "https://data.etabus.gov.hk/"
        endpoint = f"/v1/transport/kmb/stop-eta/{stop_id}"
        url = base_url + endpoint
        response = requests.get(url)
        return response.json()

    @tool
    def get_route_eta_info(route: Annotated[str, "The route number of the respective bus company"], service_type: Annotated[str, "The service type of the bus route"]) -> dict:
        """
        Retrieves the ETA information for all stops on a specific route and service type.
        """
        base_url = "https://data.etabus.gov.hk/"
        endpoint = f"/v1/transport/kmb/route-eta/{route}/{service_type}"
        url = base_url + endpoint
        response = requests.get(url)
        return response.json()

    return [get_kmb_route_list,get_route_info,get_stop_list,get_bus_stop_info,get_eta_info,get_stop_eta_info,get_route_eta_info]

tools = []
loop_funcs = [start_callback]

augmented_prompt = """"""