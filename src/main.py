import asyncio
from autogen_core import SingleThreadedAgentRuntime, AgentId

from src.agents.db_executor import DBExecutor
from src.agents.llm_agent import LLMAgent, PromptMessage
from src.agents.logger import LoggerAgent
from src.agents.result_interpreter import ResultInterpreter
from src.agents.sql_validator import SQLValidatorAgent

# for now registers all of the agents into a sequential runtime
async def main():
    user_prompt = input('Prompt:')

    runtime = SingleThreadedAgentRuntime()

    await DBExecutor().register(runtime,
                                "db_executor",
                                lambda: DBExecutor())
    
    await SQLValidatorAgent.register(runtime,
                                    "sql_validator_agent",
                                    lambda: SQLValidatorAgent(db_executor_id=AgentId("db_executor", "default")))
    
    await LLMAgent.register(runtime,
                            "llm_agent",
                            lambda: LLMAgent(validator_agent_id=AgentId("sql_validator_agent", "default")))
    
    await ResultInterpreter.register(runtime,
                                     "result_interpreter",
                                     lambda: ResultInterpreter(logger_agent_id=AgentId("logger_agent", "default")))

    await LoggerAgent.register(runtime,
                                 "logger_agent",
                                 lambda: LoggerAgent(log_file='logs/agent_logs.jsonl'))
    
    runtime.start()
    await runtime.send_message(PromptMessage(prompt=user_prompt),
                               AgentId("llm_agent", "default"))
    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main())