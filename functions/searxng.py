from agents.percive_agent import percive_agent
import os
from langchain_community.utilities import SearxSearchWrapper
from typing import Annotated, List
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from model.doc import docs
from functions.qq import QQAgent

g_agent:percive_agent = None
qq_agents: List[QQAgent]

def give_callback(agent: percive_agent, **kwargs):
    global g_agent, qq_agents
    g_agent = agent
    qq_agents = kwargs.get('functions.qq',[])
    for i in qq_agents:
        i.agent.add_tools(tool_factory(i.agent))

async def start_callback():
    pass

search = SearxSearchWrapper(searx_host=os.getenv('SEARX_URL',"http://localhost:8080"))

search_prompt=ChatPromptTemplate.from_messages(
[
    ("system", """
    <INSTRUCTION>
    You need give the content surrounded by <SEARCH_RESULT> a concise summary with detail without any prefix or suffix.
    </INSTRUCTION>
    """),
    ('user',""" 
    <SEARCH_RESULT>
    {content}
    </SEARCH_RESULT>
    """),
    ]
)

loop_funcs = [start_callback]

def tool_factory(agent: percive_agent):
    @tool
    def searx_search(query: Annotated[str, 'Keywords to search']
                    ) -> str:
        """Search Engine to search information from web."""
        results = search.run(query=query)
        result = agent.state.docs_m.add_doc([f'Original Perceive:\n{str(agent.last_perceives)}\n\nQuery:{query}\n'+results]).get_summary().to_dict()
        return result
    return [searx_search]

@tool
def searx_search(query: Annotated[str, 'Keywords to search']
                ) -> str:
    """Search Engine to search information from web."""
    results = search.run(query=query)
    result = g_agent.state.docs_m.add_doc(results,'search result').get_summary()
    return result

tools = [searx_search]

augmented_prompt = """"""