from dataclasses import dataclass
from typing import Any
from autogen_core import RoutedAgent, MessageContext, default_subscription, message_handler
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage, SystemMessage

from src.agents.logger import LogMessage

from dotenv import load_dotenv
import os

# from gpt4all import GPT4All

@dataclass 
class DBResultMessage:
    results: Any
    original_prompt: str

@default_subscription
class ResultInterpreter(RoutedAgent):
    def __init__(self, logger_agent_id):
        super().__init__("Result Interpreter Agent")
        load_dotenv()
        self.logger_agent_id = logger_agent_id

        self.model = OpenAIChatCompletionClient(
            model='gemini-2.0-flash',
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        
    
    @message_handler
    async def handle_message(self, message: DBResultMessage, ctx: MessageContext) -> None:
        data = message.results

        if not data:
            response = await self.model.create(
                messages=[
                    SystemMessage(content="The query returned no results.", source="system"),
                    UserMessage(content=f"Inform the user that no results were found. \
                                IN a sentence say why couldn't the prompt: {message.original_prompt} be answered", source="user")
                ]
            )

        else:
            # should be externalized prompt template, also to have a cleaner code
            prompt = f"""Question: {message.original_prompt}

                        Results:
                        {data}

                        Form the answer in natural language using the result.
                        If the results returns a large dictionary, summarize first few results beriefly.
                        

                        Answer:"""
            
            response = await self.model.create(
                messages=[
                    SystemMessage(content=prompt, source="system"),
                    UserMessage(content=str(data), source="user")
                ]
            )
                
        await self.send_message(
            LogMessage(prompt=message.original_prompt, answer=response.content),
            self.logger_agent_id)
        
        print(f"\n[ResultInterpreter interpreted results for prompt]: '{message.original_prompt}'")
        print(f"[Interpreted Results]:\n{response.content}\n")
        

# test local mini orca (slow but could work for easier prompts)
# import asyncio

# async def test_local_interpreter():
#     load_dotenv()

#     model = GPT4All("orca-mini-3b-gguf2-q4_0", 
#                              model_path="src/models/", 
#                              allow_download=False, 
#                              verbose=False)

#     example_results = [{'actors in database': 5462}]
    
#     prompt = f"""Question: How many actors are there in the database?

#                 Results:
#                 {example_results}

#                 Answer:"""
    
#     with model.chat_session() as session:
#         response = model.generate(prompt)
#         print(f"[Mini orca interpreted answer]: {response}")

# if __name__ == "__main__":
#     asyncio.run(test_local_interpreter())