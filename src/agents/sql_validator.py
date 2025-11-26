from autogen_core import RoutedAgent, MessageContext, default_subscription, message_handler
from pydantic import BaseModel

class SQLValidationMessage(BaseModel):
    sql_query: str
    original_prompt: str

class SQLValidatedMessage(BaseModel):
    sql_query: str
    original_prompt: str
    is_valid: bool
    error: str| None = None

@default_subscription
class SQLValidatorAgent(RoutedAgent):
    def __init__(self, db_executor_id):
        super().__init__("SQL Validator Agent")
        self.db_executor_id = db_executor_id

    @message_handler
    async def handle_message(self, message: SQLValidationMessage, ctx: MessageContext) -> None:
        sql_query = message.sql_query.strip()

        print(f"\n[SQLValidatorAgent received SQL]: {sql_query}")

        # check some potentially dangerous statements
        forbidden_statements = ['DROP', 'DELETE', 'INSERT', 'ALTER']
        if any(f in sql_query.upper() for f in forbidden_statements):
            await self.send_message(SQLValidatedMessage(
                sql_query=sql_query,
                original_prompt=message.original_prompt,
                is_valid=False,
                error="Dangerous SQL statement detected."
            ),
            ctx.sender)

            print(f"[SQLValidatorAgent detected dangerous statement]: {sql_query}\n")

            return
        
        #for multi queries 
        if sql_query.count(';') > 1:
            await self.send_message(SQLValidatedMessage(
                sql_query=sql_query,
                original_prompt=message.original_prompt,
                is_valid=False,
                error="Multiple SQL statements detected."
            ),
            ctx.sender)

            print(f"[SQLValidatorAgent detected multiple statements]: {sql_query}\n")
            return

        
        await self.send_message(SQLValidatedMessage(
            sql_query=sql_query,
            original_prompt=message.original_prompt,
            is_valid=True
        ),
        self.db_executor_id)