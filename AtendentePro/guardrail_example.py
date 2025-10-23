from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
import yaml
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class GuardrailValidationOutput(BaseModel):
    is_in_scope: bool
    reasoning: str

def load_guardrail_config():
    """Carrega configuração do guardrails_config.yaml"""
    config_paths = [
        "AtendentePro/Template/White_Martins/guardrails_config.yaml",
        "AtendentePro/Template/standard/guardrails_config.yaml",
        "guardrails_config.yaml"
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
    
    return {}

def get_triage_about():
    """Obtém o conteúdo 'about' do triage_agent"""
    config = load_guardrail_config()
    triage_about = config.get('agent_scopes', {}).get('triage_agent', {}).get('about', '')
    return triage_about.strip()

# Agente de guardrail que usa o conteúdo 'about' do triage
guardrail_agent = Agent(
    name="Triage Guardrail Check",
    instructions=f"""
    Você é um agente de validação que verifica se mensagens estão dentro do escopo do Triage Agent.
    
    CONTEXTO DO TRIAGE AGENT:
    {get_triage_about()}
    
    Sua tarefa é analisar a mensagem do usuário e determinar se ela está dentro do escopo descrito acima.
    Retorne 'is_in_scope: true' se a mensagem está relacionada aos tópicos mencionados.
    Retorne 'is_in_scope: false' se a mensagem está fora do escopo (matemática, programação, entretenimento, etc.).
    """,
    output_type=GuardrailValidationOutput,
)

@input_guardrail
async def triage_guardrail(
    ctx: RunContextWrapper[None], 
    agent: Agent, 
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """Guardrail que valida mensagens usando o contexto 'about' do triage"""
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_in_scope,
    )

# Agente de triage com guardrail
triage_agent = Agent(
    name="Triage Agent",
    instructions="Você é um agente de triagem especializado em processos fiscais e tributários da White Martins.",
    input_guardrails=[triage_guardrail],
)

async def main():
    print("🧪 Testando Sistema de Guardrails do Triage Agent")
    print("=" * 60)
    
    # Teste 1: Mensagem dentro do escopo
    print("\n1️⃣ Teste: Mensagem DENTRO do escopo")
    print("Pergunta: 'Como funciona o código IVA?'")
    try:
        result = await Runner.run(triage_agent, "Como funciona o código IVA?")
        print("✅ Guardrail permitiu a mensagem")
        print(f"Resposta: {result.final_output}")
    except InputGuardrailTripwireTriggered:
        print("❌ Guardrail bloqueou incorretamente")
    
    # Teste 2: Mensagem fora do escopo
    print("\n2️⃣ Teste: Mensagem FORA do escopo")
    print("Pergunta: 'Quem descobriu o Brasil?'")
    try:
        result = await Runner.run(triage_agent, "Quem descobriu o Brasil?")
        print("❌ Guardrail não bloqueou - comportamento incorreto")
        print(f"Resposta: {result.final_output}")
    except InputGuardrailTripwireTriggered:
        print("✅ Guardrail bloqueou corretamente a mensagem fora do escopo")
    
    # Teste 3: Mensagem de matemática
    print("\n3️⃣ Teste: Mensagem de matemática")
    print("Pergunta: 'Resolva a equação 2x + 5 = 11'")
    try:
        result = await Runner.run(triage_agent, "Resolva a equação 2x + 5 = 11")
        print("❌ Guardrail não bloqueou - comportamento incorreto")
        print(f"Resposta: {result.final_output}")
    except InputGuardrailTripwireTriggered:
        print("✅ Guardrail bloqueou corretamente a mensagem de matemática")
    
    # Teste 4: Mensagem de programação
    print("\n4️⃣ Teste: Mensagem de programação")
    print("Pergunta: 'Como criar uma API em Python?'")
    try:
        result = await Runner.run(triage_agent, "Como criar uma API em Python?")
        print("❌ Guardrail não bloqueou - comportamento incorreto")
        print(f"Resposta: {result.final_output}")
    except InputGuardrailTripwireTriggered:
        print("✅ Guardrail bloqueou corretamente a mensagem de programação")
    
    print("\n🎯 Teste concluído!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())