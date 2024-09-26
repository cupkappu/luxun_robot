from agents.percive_agent import percive_agent
from typing import Annotated
from langchain.tools import tool
import os

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
    if len(g_agent.state.note) < int(os.getenv('NOTE_MAX_NUMBER',10)):
        g_agent.state.note.append({
            'title': title,
            'content': content
        })
        return f'Note {title} added.'
    else:
        return f'Note {title} add fail, reached the max limit. Try to delete some unimportant notes.'

@tool
def delete_note(title: Annotated[str, 'The title of the note.']):
    """Delete a note from <NOTE>."""
    for i in range(len(g_agent.state.note)):
        if g_agent.state.note[i]['title'] == title:
            del g_agent.state.note[i]
            return f'Note {title} deleted.'
    return f'Note {title} not found.'

tools = [add_note,delete_note]

augmented_prompt = """The content surrounded by the <NOTE> tag is your own notes. Add notes when necessary and don’t add notes when not necessary."""