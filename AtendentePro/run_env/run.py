from __future__ import annotations

import argparse
import asyncio

from agents import Runner, InputGuardrailTripwireTriggered
from agents.items import TResponseInputItem
from agents.stream_events import AgentUpdatedStreamEvent, RawResponsesStreamEvent, RunItemStreamEvent
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent

from pathlib import Path
import sys

from dotenv import load_dotenv

load_dotenv()

from agents import  set_default_openai_client, set_default_openai_api
from AtendentePro.utils.openai_client import get_async_client, get_provider


client = get_async_client()
provider = get_provider()

set_default_openai_client(client)
set_default_openai_api("chat_completions")

print(f"🔧 Usando provider OpenAI: {provider}")


if __package__ is None or __package__ == "":
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root.parent) not in sys.path:
        sys.path.append(str(package_root.parent))
    from AtendentePro import configure_agent_network  # type: ignore
    from AtendentePro.Answer.answer_agent import answer_agent  # type: ignore
    from AtendentePro.Confirmation.confirmation_agent import confirmation_agent  # type: ignore
    from AtendentePro.Flow.flow_agent import flow_agent  # type: ignore
    from AtendentePro.Interview.interview_agent import interview_agent  # type: ignore
    from AtendentePro.Knowledge.knowledge_agent import knowledge_agent  # type: ignore
    from AtendentePro.Triage.triage_agent import triage_agent  # type: ignore
    from AtendentePro.Usage.usage_agent import usage_agent  # type: ignore
    from AtendentePro.guardrail_messages import get_guardrail_message  # type: ignore
else:
    from AtendentePro import configure_agent_network
    from AtendentePro.Answer.answer_agent import answer_agent
    from AtendentePro.Confirmation.confirmation_agent import confirmation_agent
    from AtendentePro.Flow.flow_agent import flow_agent
    from AtendentePro.Interview.interview_agent import interview_agent
    from AtendentePro.Knowledge.knowledge_agent import knowledge_agent
    from AtendentePro.Triage.triage_agent import triage_agent
    from AtendentePro.Usage.usage_agent import usage_agent
    from AtendentePro.guardrail_messages import get_guardrail_message


AGENT_REGISTRY = {
    "triage": triage_agent,
    "flow": flow_agent,
    "interview": interview_agent,
    "answer": answer_agent,
    "confirmation": confirmation_agent,
    "knowledge": knowledge_agent,
    "usage": usage_agent,
}


async def run_demo_loop_with_guardrails(agent, *, stream: bool = True, context=None):
    """Run a REPL loop with guardrails handling.
    
    This custom version handles InputGuardrailTripwireTriggered exceptions
    by providing user-friendly messages from client-specific configuration files.
    """
    current_agent = agent
    input_items: list[TResponseInputItem] = []
    
    print(f"🤖 Agente {agent.name} iniciado. Digite 'exit' ou 'quit' para sair.\n")
    
    while True:
        try:
            user_input = input(" > ")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Até logo!")
            break
            
        if user_input.strip().lower() in {"exit", "quit"}:
            print("👋 Até logo!")
            break
            
        if not user_input:
            continue

        input_items.append({"role": "user", "content": user_input})

        try:
            result = Runner.run_streamed(current_agent, input=input_items, context=context)
            async for event in result.stream_events():
                if isinstance(event, RawResponsesStreamEvent):
                    if isinstance(event.data, ResponseTextDeltaEvent):
                        print(event.data.delta, end="", flush=True)
                elif isinstance(event, RunItemStreamEvent):
                    if event.item.type == "tool_call_item":
                        print("\n[tool called]", flush=True)
                    elif event.item.type == "tool_call_output_item":
                        print(f"\n[tool output: {event.item.output}]", flush=True)
                elif isinstance(event, AgentUpdatedStreamEvent):
                    print(f"\n[Agent updated: {event.new_agent.name}]", flush=True)
            print()
            
        except InputGuardrailTripwireTriggered as e:
            # Handle guardrail tripwire with client-specific message
            guardrail_message = get_guardrail_message("out_of_scope", detailed=True)
            print(guardrail_message)
            
            # Add the guardrail response to conversation history
            input_items.append({
                "role": "assistant", 
                "content": get_guardrail_message("out_of_scope", detailed=False)
            })
            continue

        current_agent = result.last_agent
        input_items = result.to_input_list()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an AtendentePro agent.")
    parser.add_argument(
        "agent",
        choices=AGENT_REGISTRY.keys(),
        nargs="?",
        default="triage",
        help="Agent to start (default: triage)",
    )
    return parser.parse_args()


def main() -> None:
    configure_agent_network()
    #args = parse_args()
    #agent = AGENT_REGISTRY[args.agent]
    agent = AGENT_REGISTRY["interview"]
    print(f"Iniciando sessão com o agente: {agent.name}\n")
    
    asyncio.run(run_demo_loop_with_guardrails(agent))


if __name__ == "__main__":
    main()
