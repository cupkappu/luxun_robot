from agents.percive_agent import percive_agent
from functions.qq import QQAgent
from typing import Annotated, List
from langchain.tools import tool
from langchain_core.documents import Document
from prompts.sum_prompt import map_prompt,reduce_prompt
from langchain_core.output_parsers import StrOutputParser

g_agent:percive_agent = None
qq_agents: List[QQAgent]


def give_callback(agent: percive_agent, **kwargs):
    global g_agent, qq_agents
    g_agent = agent
    qq_agents = kwargs.get('functions.qq',[])
    for i in qq_agents:
        i.agent.add_tools(tool_factory(i.agent))
        i.agent.augmented_prompts['summary_time_to_time_message'] = augmented_prompt

async def start_callback():
    pass

def tool_factory(agent:percive_agent):
    @tool
    def summary_time_to_time_message(start_time: Annotated[str, 'Start time in format yyyy-MM-dd HH:mm:ss'], 
                                     end_time: Annotated[str, 'End time in format yyyy-MM-dd HH:mm:ss']):
        """Summarizes messages between start_time and end_time."""
        map_chain = map_prompt | agent.llm | StrOutputParser()
        reduce_chain = reduce_prompt | agent.llm | StrOutputParser()
        messages = agent.state.current_memory_list.get_time_memorys(start_time,end_time)
        messages_text = "\n".join([str(message) for message in messages])
        chunk_size = 5000
        chunks = [Document(messages_text[i:i + chunk_size]) for i in range(0, len(messages_text), chunk_size)]
        map_results = [map_chain.invoke({'context':chunk}) for chunk in chunks]
        summary = reduce_chain.invoke({'context':map_results})
        return summary
    return [summary_time_to_time_message]

tools = []
loop_funcs = []

augmented_prompt = """You need use summary_time_to_time_message to summarize the messages between the start time and end time when user's chat message summarization query have the time information."""