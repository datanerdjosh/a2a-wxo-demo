"""Minimal Hello World A2A server — protocol version 0.3.0.

Compatible with IBM watsonx Orchestrate SaaS which supports A2A 0.2.1 and 0.3.0.
Returns a hardcoded Hello World response to any input — no LLM required.
"""
import uuid
import uvicorn

from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.apps.jsonrpc.starlette_app import A2AStarletteApplication
from a2a.server.events.event_queue import EventQueue
from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import AgentCard, Part, TextPart
from a2a.utils.message import get_message_text
from starlette.middleware.cors import CORSMiddleware

PORT = 9999


class HelloWorldExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        raw_text = get_message_text(context.message) if context.message else ''
        response_text = f'Hello, World! I have received your request ({raw_text})'

        updater = TaskUpdater(
            event_queue,
            task_id=context.task_id or str(uuid.uuid4()),
            context_id=context.context_id or str(uuid.uuid4()),
        )
        await updater.submit()
        await updater.add_artifact([Part(root=TextPart(text=response_text))])
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError('Cancel not supported')


agent_card = AgentCard.model_validate({
    'name': 'Hello World Agent',
    'description': 'A minimal hello world A2A agent for testing with IBM watsonx Orchestrate.',
    'url': f'http://127.0.0.1:{PORT}/',
    'preferredTransport': 'JSONRPC',
    'protocolVersion': '0.3.0',
    'version': '1.0.0',
    'capabilities': {
        'streaming': True,       # Must be True — Orchestrate always uses the streaming endpoint
        'pushNotifications': False,
        'stateTransitionHistory': False,
    },
    'defaultInputModes': ['text/plain'],
    'defaultOutputModes': ['text/plain'],
    'skills': [{
        'id': 'hello_world',
        'name': 'Hello World',
        'description': 'Responds with a Hello World message to any input.',
        'tags': ['hello', 'demo'],
        'inputModes': ['text/plain'],
        'outputModes': ['text/plain'],
        'examples': ['hello', 'hi there'],
    }],
})


if __name__ == '__main__':
    handler = DefaultRequestHandler(HelloWorldExecutor(), InMemoryTaskStore())
    app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=handler
    ).build(rpc_url='/')          # Must be '/' — Orchestrate posts to the root of your URL
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_methods=['*'],
        allow_headers=['*'],
    )
    print(f'Hello World Agent (A2A 0.3.0) listening on http://127.0.0.1:{PORT}')
    uvicorn.run(app, host='127.0.0.1', port=PORT)
