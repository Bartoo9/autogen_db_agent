from dataclasses import dataclass
from typing import Any
from autogen_core import RoutedAgent, DefaultTopicId, MessageContext, default_subscription, message_handler

@dataclass 
class DBResultMessage:
    results: Any
    original_prompt: str

@default_subscription
class ResultInterpreter(RoutedAgent):
    def __init__(self):
        super().__init__("Result Interpreter Agent")
    
    @message_handler
    async def handle_message(self, message: DBResultMessage, ctx: MessageContext) -> None:
        data = message.results

        if not data:
            readable = "No results found"
        else:
            readable = "\n".join([", ".join(f"{k}: {v}" for k,v in row.items()) for row in data])
        
        print(f"\n[ResultInterpreter interpreted results for prompt]: '{message.original_prompt}'")
        print(f"[Interpreted Results]:\n{readable}\n")