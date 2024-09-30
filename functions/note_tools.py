from agents.percive_agent import percive_agent
from typing import Annotated, List
from langchain.tools import tool
import os
from functions.qq import QQAgent

g_agent:percive_agent = None
qq_agents: List[QQAgent]

def give_callback(agent: percive_agent, **kwargs):
    global g_agent, qq_agents
    g_agent = agent
    qq_agents = kwargs.get('functions.qq',[])
    for i in qq_agents:
        i.agent.add_tools(tool_factory(i.agent.state.docs_m))
        i.agent.augmented_prompts['note_tools'] = augmented_prompt

async def start_callback():
    pass

def tool_factory(agent:percive_agent):
    @tool
    def add_note(title: Annotated[str, 'The title of your note, make it simple and straight and unique.'],
            content: Annotated[str,"The content you want to make note."]):
        """Add a note to <NOTE>."""
        if len(agent.state.note) < int(os.getenv('NOTE_MAX_NUMBER',10)):
            agent.state.note.append({
                'title': title,
                'content': content
            })
            return f'Note {title} added.'
        else:
            return f'Note {title} add fail, reached the max limit. Try to delete some unimportant notes.'

    @tool
    def delete_note(title: Annotated[str, 'The title of the note.']):
        """Delete a note from <NOTE>."""
        for i in range(len(agent.state.note)):
            if agent.state.note[i]['title'] == title:
                del agent.state.note[i]
                return f'Note {title} deleted.'
        return f'Note {title} not found.'
    return [add_note,delete_note]

tools = []
loop_funcs = [start_callback]

augmented_prompt = """The content surrounded by the <NOTE> tag is your own notes. Don't add notes when not necessary."""