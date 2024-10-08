from agents.percive_agent import percive_agent
from functions.qq import QQAgent
from typing import Annotated, List
from langchain.tools import tool
from datetime import datetime
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from prompts.sum_prompt import prompt

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

def tool_factory(agent:percive_agent):
    @tool
    def summary_time_to_time_message(start_time: Annotated[str, 'Start time in format yyyy-MM-dd HH:mm:ss'], 
                                     end_time: Annotated[str, 'End time in format yyyy-MM-dd HH:mm:ss']):
        """Summarizes messages between start_time and end_time."""
        messages = agent.state.current_memory_list.get_time_memorys(start_time,end_time)  # Replace with actual data source
        messages_text = "\n".join(str(messages))
        chunk_size = 100000
        chunks = [Document(messages_text[i:i + chunk_size]) for i in range(0, len(messages_text), chunk_size)]
        chain = create_stuff_documents_chain(llm=agent.llm,prompt=prompt)
        summary = chain.invoke({'context':chunks})
        return summary
    return [summary_time_to_time_message]

tools = []
loop_funcs = []

augmented_prompt = """"""