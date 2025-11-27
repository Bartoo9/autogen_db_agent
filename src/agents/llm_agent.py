from dataclasses import dataclass
from autogen_core import RoutedAgent, MessageContext, default_subscription, message_handler
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage, SystemMessage

from src.agents.sql_validator import SQLValidationMessage

import os
from dotenv import load_dotenv

# from gpt4all import GPT4All

@dataclass 
class PromptMessage:
    prompt: str

@default_subscription
class LLMAgent(RoutedAgent):
    def __init__(self, validator_agent_id):
        super().__init__("LLM Agent")
        load_dotenv()

        self.validator_agent_id = validator_agent_id

        # works for any openai compatible model, here gemini used 
        self.model = OpenAIChatCompletionClient(
            model='gemini-2.0-flash',
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        
        # static schmea - should be updated to be schema agostic (perhaps an agent that fetches schema on init)
        with open("src/schema/1-postgres-sakila-schema.sql", "r") as f:
            self.schema = f.read()
        
        # prompt engineering for sql generation, should be externalized later
        self.system_prompt = f"""
                            You are a SQL generation assistant for the Sakila PostgreSQL database.

                            RULES:
                            - Return ONLY SQL.
                            - No Markdown, no backticks, no explanations.
                            - Use only tables/columns from this schema:
                            - You MUST always return exactly one SQL statement.
                            - If multiple values are needed, use subqueries in a single SELECT.
                            - Use aliases when using subqueries to retrive multiple results.
                            - treat 'today' as sakila database current date: 2006-02-14.

                            Schema:
                            {self.schema}
                            """
        
    @message_handler
    async def handle_message(self, message: PromptMessage, ctx: MessageContext) -> None:
        print(f"\n[LLMAgent received prompt]: {message.prompt}")

        sql_query = await self.prompt_to_sql(message.prompt)
        print(f"[LLMAgent generated SQL]: {sql_query}")

        await self.send_message(
            SQLValidationMessage(sql_query=sql_query, original_prompt=message.prompt), 
                                self.validator_agent_id)
    
    async def prompt_to_sql(self, prompt: str) -> str:
        response = await self.model.create(
            messages=[
                SystemMessage(content=self.system_prompt, source="system"),
                UserMessage(content=prompt, source="user")
            ]
        )
        
        # response query clean, was returning mkd format
        if response.content.startswith("```"):
            response.content = response.content.lstrip("`")
            response.content = response.content.replace("sql", "", 1).replace("SQL", "", 1)
            response.content = response.content.rstrip("`")

        return response.content.strip()

        
# test local mini orca (slow but could work for easier prompts)
# import asyncio

# async def test_local_model():
#     load_dotenv()
#     model = GPT4All("orca-mini-3b-gguf2-q4_0", model_path="src/models/", allow_download=False, verbose=False)
#     schema = open("src/models/sakila_table.sql", "r").read()

#     system_prompt = f"""You are a SQL generation assistant for the Sakila PostgreSQL database.
#                         Output only the SQL query without any explanations.

#                         {schema}
#                         """
    
#     with model.chat_session():
#         print(model.generate(system_prompt + "User: How many films are in the inventory?"))

# if __name__ == "__main__":
#     asyncio.run(test_local_model())