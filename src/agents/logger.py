from dataclasses import dataclass
from autogen_core import RoutedAgent, MessageContext, default_subscription, message_handler
import json
import os

@dataclass
class LogMessage:
    prompt: str
    answer: str

@default_subscription
class LoggerAgent(RoutedAgent):
    def __init__(self, log_file='agent_logs.jsonl'):
        super().__init__("Logger Agent")
        self.log_file = log_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    @message_handler
    async def handle_message(self, message: LogMessage, ctx: MessageContext) -> None:
        log_entry = {
            "prompt": message.prompt,
            "answer": message.answer
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        print(f"[LoggerAgent] Logged interaction to {self.log_file}")

