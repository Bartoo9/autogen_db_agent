from dataclasses import dataclass
from typing import Callable 

from autogen_core import DefaultTopicId, MessageContext, RoutedAgent, default_subscription, message_handler

@dataclass
class Message:
    content: int

@default_subscription
class Modifier(RoutedAgent):
    def __init__(self, modified_val: Callable[[int], int]) -> None:
        super().__init__('modifier agent')
        self._modified_val = modified_val

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> None:
        val = self._modified_val(message.content)
        print(f"{'-'*80}\n{self.id.type} received: {message.content}\nModified to: {val}")
        await self.publish_message(Message(content=val), DefaultTopicId())

@default_subscription
class Checker(RoutedAgent):
    def __init__(self, run_until: Callable[[int], bool]) -> None:
        super().__init__('checker agent')
        self._run_until = run_until

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> None:
        if not self._run_until(message.content):
            print(f"{'-'*80}\nChecker received: {message.content}\n passed the check, continue")
            await self.publish_message(Message(content=message.content), DefaultTopicId())
        else:
            print(f"{'-'*80}\nChecker received: {message.content}\n failed the check")


from autogen_core import AgentId, SingleThreadedAgentRuntime
import asyncio

async def main() -> None:
    runtime = SingleThreadedAgentRuntime()

    await Modifier.register(
        runtime,
        'modifier',
        lambda: Modifier(modified_val=lambda x: x - 1),
    )

    await Checker.register(
        runtime,
        'checker',
        lambda: Checker(run_until=lambda x: x <= 0),
    )

    runtime.start()
    await runtime.send_message(Message(10), AgentId('checker', 'default'))
    await runtime.stop_when_idle()
    
if __name__ == '__main__':
    asyncio.run(main())