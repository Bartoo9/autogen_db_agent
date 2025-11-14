import asyncio
from autogen_core import SingleThreadedAgentRuntime, AgentId

from src.agents.db_executor import DBExecutor
from src.agents.llm_agent import LLMAgent, PromptMessage


async def main():
    runtime = SingleThreadedAgentRuntime()

    await DBExecutor().register(runtime,
                                "db_executor",
                                lambda: DBExecutor())
    db_executor_id = AgentId("db_executor", "default")

    await LLMAgent.register(runtime,
                            "llm_agent",
                            lambda: LLMAgent(db_executor_id=db_executor_id))
    
    runtime.start()

    await runtime.send_message(PromptMessage(prompt="How many actors are there in the databse?"),
                               AgentId("llm_agent", "default"))
    
    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main())