from agents.percive_agent import percive_agent
from typing import Annotated
from langchain.tools import tool

g_agent:percive_agent = None

def give_callback(agent: percive_agent):
    global g_agent
    g_agent = agent

async def start_callback():
    pass

@tool
def add_note(title: Annotated[str, 'The title of your note, make it simple and straight and unique.'],
        content: Annotated[str,"The content you want to make note."]):
    """Add a note to <NOTE>."""
    g_agent.state.note.append({
        'title': title,
        'content': content
    })
    return f'Note {title} added.'

@tool
def delete_note(title: Annotated[str, 'The title of the note.']):
    """Delete a note from <NOTE>."""
    for i in range(len(g_agent.state.note)):
        if g_agent.state.note[i]['title'] == title:
            del g_agent.state.note[i]
            break
    return f'Note {title} deleted.'

tools = {'add_note':add_note,'delete_note':delete_note}