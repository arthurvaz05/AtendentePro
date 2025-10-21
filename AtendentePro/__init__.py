from __future__ import annotations
from dotenv import load_dotenv

load_dotenv()

from agents import  set_default_openai_client, set_default_openai_api
from AtendentePro.agent_network import configure_agent_network
from AtendentePro.utils.openai_client import get_async_client

client = get_async_client()

set_default_openai_client(client)
set_default_openai_api("chat_completions")

configure_agent_network()
