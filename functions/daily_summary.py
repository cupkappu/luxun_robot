from agents.percive_agent import percive_agent
from functions.qq import QQAgent
from typing import Annotated, List
from langchain.tools import tool
from datetime import datetime
from langchain.chains import SummarizationChain

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
        start_time_datetime = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time_datetime = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        messages = agent.state.current_memory_list.get_time_memorys(start_time_datetime,end_time_datetime)  # Replace with actual data source
        messages_text = "\n".join(str(messages))
        summarization_chain = SummarizationChain(llm=agent.llm)
        summary = summarization_chain.run(messages_text)
        return summary
    return [summary_time_to_time_message]

tools = []
loop_funcs = []

augmented_prompt = """"""