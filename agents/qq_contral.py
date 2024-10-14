from typing import Dict,List
from .percive_agent import percive_agent
from langchain.tools import StructuredTool
from textwrap import dedent
class cmd:
    name:str = ""
    desc:str = ""
    run: callable
    def __init__(self,name:str,desc:str,arg_desc:str, run:callable):
        self.name = name
        self.desc = desc
        self.run = run
        self.arg_desc = arg_desc

class cmd_processer:
    cmds:Dict[str,cmd] = {}
    kwargs:Dict[str,any] = {}
    agent: percive_agent

    def __init__(self, cmds:Dict[str,cmd], agent: percive_agent):
        self.cmds = cmds
        self.agent = agent
        self.kwargs = kwargs
    
    def register(self,tools:List[StructuredTool]):
        self.cmds.update({i.name: cmd(i.name,i.description,i.args,i.func) for i in tools})

    def run(self,cmd:str,*args:List[str],**kwargs):
        try:
            if cmd in self.cmds:
                return self.cmds[cmd].run(*args,**self.kwargs)
            else:
                return f"Command {cmd} not found."
        except Exception as e:
            return f"Error: {e}"
            
    def process(self,cmd:str):
        cmd = cmd.split(" ")
        if cmd[0].split("!")[1] == "help":
            if len(cmd) == 1:
                return self.help()
            return self.help(cmd[1])
        else:
            return self.run(cmd[0].split("!")[1],*cmd[1:])

    def help(self,cmd:str = None):
        if len(self.cmds) == 0:
            return "No command registered."
        if cmd == None:
            return dedent(
f"""        Command List:
            {", ".join(self.cmds.keys())}
            """)
        else:
            if cmd in self.cmds:
                arg_desc = self.cmds[cmd].arg_desc
                formatted_arg_desc = "\n".join([f"{key}: {value['title']}\n  Description: {value['description']}\n  Type: {value['type']}" for key, value in arg_desc.items()])
                return dedent(f"""
                Command: {cmd}
                Description: {self.cmds[cmd].desc}
                Arguments:
                {formatted_arg_desc}
                """)
            else:
                return f"Command {cmd} not found."