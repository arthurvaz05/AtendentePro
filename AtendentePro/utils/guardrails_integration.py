"""
Exemplo de integração do sistema de guardrails com os agentes existentes
"""

import asyncio
from guardrails import GuardrailSystem, GuardrailOutput


class GuardrailIntegration:
    """Integração do sistema de guardrails com os agentes"""
    
    def __init__(self, template_path: str = None):
        """
        Inicializa o sistema de guardrails
        
        Args:
            template_path: Caminho para configuração específica do template
        """
        if template_path:
            self.guardrail_system = GuardrailSystem(template_path)
        else:
            self.guardrail_system = GuardrailSystem()
    
    async def check_before_agent(
        self, 
        message: str, 
        agent_name: str,
        confidence_threshold: float = 0.7
    ) -> tuple[bool, GuardrailOutput]:
        """
        Verifica se a mensagem está no escopo antes de processar com o agente
        
        Args:
            message: Mensagem do usuário
            agent_name: Nome do agente
            confidence_threshold: Limiar de confiança para aceitar
            
        Returns:
            Tuple (deve_continuar, resultado_guardrail)
        """
        result = await self.guardrail_system.evaluate_message(message, agent_name)
        
        # Se está no escopo e tem confiança suficiente, permite continuar
        should_continue = (
            result.is_in_scope and 
            result.confidence >= confidence_threshold
        )
        
        return should_continue, result
    
    async def handle_out_of_scope(
        self, 
        result: GuardrailOutput, 
        agent_name: str
    ) -> str:
        """
        Trata mensagens fora do escopo
        
        Args:
            result: Resultado do guardrail
            agent_name: Nome do agente
            
        Returns:
            Mensagem de resposta apropriada
        """
        if result.suggested_action == "refuse":
            return (
                "Desculpe, mas não posso ajudá-lo com essa consulta. "
                "Estou aqui para auxiliar com questões relacionadas aos produtos "
                "e serviços da White Martins. Como posso ajudá-lo com nossos "
                "equipamentos pneumáticos ou sistemas de automação?"
            )
        elif result.suggested_action == "redirect":
            return (
                "Parece que sua consulta pode ser melhor atendida por outro agente. "
                "Vou redirecioná-lo para o agente mais apropriado. "
                "Por favor, reformule sua pergunta focando em produtos ou serviços "
                "da White Martins."
            )
        else:
            return (
                "Entendi sua consulta. Embora não seja exatamente minha especialidade, "
                "vou tentar ajudá-lo da melhor forma possível. "
                "Você poderia fornecer mais detalhes sobre sua necessidade?"
            )


# Exemplo de uso com agentes específicos
async def example_triage_with_guardrails():
    """Exemplo de uso do triage agent com guardrails"""
    integration = GuardrailIntegration("Template/White_Martins/guardrails_config.yaml")
    
    test_messages = [
        "Preciso de uma válvula pneumática para minha aplicação industrial",
        "Como resolver 2x + 5 = 11?",  # Fora do escopo
        "Qual é o preço de um cilindro pneumático?",
        "Me ajude com programação Python",  # Fora do escopo
        "Quero informações sobre compressores White Martins"
    ]
    
    agent_name = "triage_agent"
    
    for message in test_messages:
        print(f"\n--- Testando: {message} ---")
        
        should_continue, result = await integration.check_before_agent(
            message, agent_name
        )
        
        print(f"Escopo: {result.is_in_scope}")
        print(f"Confiança: {result.confidence:.2f}")
        print(f"Ação sugerida: {result.suggested_action}")
        print(f"Razão: {result.reasoning}")
        
        if should_continue:
            print("✅ Processando com o agente...")
            # Aqui chamaria o agente real
        else:
            print("❌ Mensagem fora do escopo")
            response = await integration.handle_out_of_scope(result, agent_name)
            print(f"Resposta: {response}")


# Exemplo de integração com o sistema de agentes existente
class AgentWithGuardrails:
    """Wrapper para agentes com guardrails integrados"""
    
    def __init__(self, agent, template_path: str = None):
        self.agent = agent
        self.guardrail_integration = GuardrailIntegration(template_path)
    
    async def process_with_guardrails(
        self, 
        message: str, 
        agent_name: str = None
    ) -> str:
        """
        Processa mensagem com verificação de guardrails
        
        Args:
            message: Mensagem do usuário
            agent_name: Nome do agente (se não fornecido, usa o nome do agente)
            
        Returns:
            Resposta processada
        """
        if not agent_name:
            agent_name = getattr(self.agent, 'name', 'unknown_agent')
        
        should_continue, result = await self.guardrail_integration.check_before_agent(
            message, agent_name
        )
        
        if should_continue:
            # Processa normalmente com o agente
            return await self.agent.process(message)
        else:
            # Trata mensagem fora do escopo
            return await self.guardrail_integration.handle_out_of_scope(
                result, agent_name
            )


if __name__ == "__main__":
    # Executa exemplo
    asyncio.run(example_triage_with_guardrails())

