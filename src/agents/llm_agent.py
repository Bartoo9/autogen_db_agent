from dataclasses import dataclass
from autogen_core import RoutedAgent, DefaultTopicId, MessageContext, default_subscription, message_handler
from src.agents.db_executor import SQLMessage

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage
import os
from dotenv import load_dotenv

from gpt4all import GPT4All

@dataclass 
class PromptMessage:
    prompt: str

@default_subscription
class LLMAgent(RoutedAgent):
    def __init__(self, db_executor_id):
        super().__init__("LLM Agent")
        load_dotenv()

        self.db_executor_id = db_executor_id
        self.model = GPT4All("gpt4all-mini-orca", model_path="/home/barto/Downloads/orca-mini-3b-gguf2-q4_0.gguf")

    @message_handler
    async def handle_message(self, message: PromptMessage, ctx: MessageContext) -> None:
        print(f"\n[LLMAgent received prompt]: {message.prompt}")

        sql_query = self.prompt_to_sql(message.prompt)
        print(f"[LLMAgent generated SQL]: {sql_query}")

        await self.send_message(SQLMessage(query=sql_query, original_prompt=message.prompt), 
                                self.db_executor_id)
    
    def prompt_to_sql(self, prompt: str) -> str:
        prompt_lower = prompt.lower()

        # 1️⃣ Actor brings the highest income
        if "actor brings the highest income" in prompt_lower:
            return """
            SELECT a.first_name, a.last_name, SUM(p.amount) AS total_income
            FROM actor a
            JOIN film_actor fa ON a.actor_id = fa.actor_id
            JOIN film f ON fa.film_id = f.film_id
            JOIN inventory i ON f.film_id = i.film_id
            JOIN rental r ON i.inventory_id = r.inventory_id
            JOIN payment p ON r.rental_id = p.rental_id
            GROUP BY a.actor_id, a.first_name, a.last_name
            ORDER BY total_income DESC
            LIMIT 1;
            """

        # 2️⃣ Earned per movie yesterday
        elif "earned per movie yesterday" in prompt_lower:
            return """
            SELECT f.title, SUM(p.amount) AS revenue
            FROM payment p
            JOIN rental r ON p.rental_id = r.rental_id
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            WHERE p.payment_date::date = CURRENT_DATE - INTERVAL '1 day'
            GROUP BY f.film_id, f.title
            ORDER BY revenue DESC;
            """

        # 3️⃣ Location that might need to be closed (example: least revenue)
        elif "location might need to be closed" in prompt_lower:
            return """
            SELECT s.store_id, SUM(p.amount) AS total_revenue
            FROM payment p
            JOIN rental r ON p.rental_id = r.rental_id
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN store s ON i.store_id = s.store_id
            GROUP BY s.store_id
            ORDER BY total_revenue ASC
            LIMIT 1;
            """

        # Default fallback
        else:
            return "SELECT 'No mock SQL available for this prompt' AS result;"

import asyncio

async def test_openai_model():
    load_dotenv()
    model = GPT4All("orca-mini-3b-gguf2-q4_0", model_path="src/models/", allow_download=False, verbose=True)
    with model.chat_session():
        print(model.generate("If I give you a schema for an SQL database, can you generate SQL queries for me?"))

if __name__ == "__main__":
    asyncio.run(test_openai_model())