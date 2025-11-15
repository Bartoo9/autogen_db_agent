from dataclasses import dataclass
from autogen_core import RoutedAgent, DefaultTopicId, MessageContext, default_subscription, message_handler

from src.utils.db_connection import execute_query
from src.agents.result_interpreter import DBResultMessage

import decimal 
import asyncpg

# db query executor agent
@dataclass
class SQLMessage:
    query: str
    original_prompt: str = "unknown"

@default_subscription
class DBExecutor(RoutedAgent):
    def __init__(self):
        super().__init__("DB Executor AGent")

    @message_handler
    async def handle_message(self, message: SQLMessage, ctx: MessageContext) -> None:
        print(f"\n[DBExecutor received query]: {message.query}")

        try:
            results = await execute_query(message.query)

            def sanitize(obj):
                if isinstance(obj, list):
                    return [sanitize(o) for o in obj]
                elif isinstance(obj, dict):
                    return {k: sanitize(v) for k, v in obj.items()}
                elif isinstance(obj, decimal.Decimal):
                    return str(obj)
                else:
                    return obj
                
            results = sanitize(results)
            
            print(f"[DBExecutor query results]: {results}\n")

            await self.publish_message(
                DBResultMessage(results=results, original_prompt=message.original_prompt),
                DefaultTopicId()
            )

            
        except asyncpg.PostgresError:
            result = 'Query could not be executed.'
