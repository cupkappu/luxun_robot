from agents.percive_agent import percive_agent
import os
from langchain_community.utilities import SearxSearchWrapper
from typing import Annotated
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate

g_agent:percive_agent = None

def give_callback(agent: percive_agent):
    global g_agent
    g_agent = agent

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


@tool
def searx_search(query: Annotated[str, 'Keywords to search']
                ) -> str:
    """Search Engine to search information from web."""
    results = search.run(query=query)
    result = g_agent.state.docs_m.add_doc(results).get_summary()
    return result

tools = [searx_search]

augmented_prompt = """"""