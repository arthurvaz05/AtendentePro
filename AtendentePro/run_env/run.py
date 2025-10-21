from __future__ import annotations

import argparse
import asyncio

from agents import run_demo_loop

from pathlib import Path
import sys

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
else:
    from AtendentePro import configure_agent_network
    from AtendentePro.Answer.answer_agent import answer_agent
    from AtendentePro.Confirmation.confirmation_agent import confirmation_agent
    from AtendentePro.Flow.flow_agent import flow_agent
    from AtendentePro.Interview.interview_agent import interview_agent
    from AtendentePro.Knowledge.knowledge_agent import knowledge_agent
    from AtendentePro.Triage.triage_agent import triage_agent
    from AtendentePro.Usage.usage_agent import usage_agent


AGENT_REGISTRY = {
    "triage": triage_agent,
    "flow": flow_agent,
    "interview": interview_agent,
    "answer": answer_agent,
    "confirmation": confirmation_agent,
    "knowledge": knowledge_agent,
    "usage": usage_agent,
}


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
    args = parse_args()
    agent = AGENT_REGISTRY[args.agent]
    print(f"Iniciando sessão com o agente: {agent.name}\n")
    
    asyncio.run(run_demo_loop(agent))


if __name__ == "__main__":
    main()