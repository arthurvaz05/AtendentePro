"""
Sistema de Guardrails Genérico para AtendentePRO
Utiliza chatcompletion para avaliar se mensagens estão de acordo com o escopo dos agentes
"""

import asyncio
import os
import yaml
from typing import Dict, Any, Optional
from pydantic import BaseModel
from openai import AsyncOpenAI
from pathlib import Path
from AtendentePro.utils.openai_client import get_async_client


class GuardrailOutput(BaseModel):
    """Output do guardrail"""
    reasoning: str
    is_in_scope: bool
    confidence: float
    suggested_action: str


class GuardrailConfig:
    """Configuração dos guardrails"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        self.client = get_async_client()
        #self.client = AsyncOpenAI()
    
    def _find_config_file(self) -> str:
        """Encontra o arquivo de configuração apropriado"""
        # Ordem de prioridade: específico do cliente -> standard -> fallback
        config_paths = [
            "AtendentePro/Template/White_Martins/guardrails_config.yaml",
            "AtendentePro/Template/standard/guardrails_config.yaml",
            "guardrails_config.yaml"
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                return path
        
        # Se nenhum arquivo for encontrado, retorna o primeiro como fallback
        return config_paths[0]
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração dos guardrails"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            # Fallback para configuração genérica
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão quando não há arquivo específico"""
        return {
            "agent_scopes": {
                "triage_agent": {
                    "about": "O Triage Agent é responsável por rotear conversas para os agentes especializados. "
                            "Ele deve identificar se a pergunta do usuário se encaixa nos tópicos disponíveis no sistema. "
                            "Não deve responder sobre matemática, lição de casa, trabalho escolar, programação ou jogos."
                }
            }
        }
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Obtém configuração específica de um agente"""
        return self.config.get("agent_scopes", {}).get(agent_name, {})


class GuardrailSystem:
    """Sistema principal de guardrails"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = GuardrailConfig(config_path)
    
    async def evaluate_message(
        self, 
        message: str, 
        agent_name: str,
        model: str = "gpt-4o-mini"
    ) -> GuardrailOutput:
        """
        Avalia se uma mensagem está de acordo com o escopo do agente
        
        Args:
            message: Mensagem do usuário
            agent_name: Nome do agente que vai processar
            model: Modelo a ser usado para avaliação
            
        Returns:
            GuardrailOutput com resultado da avaliação
        """
        agent_config = self.config.get_agent_config(agent_name)
        
        if not agent_config:
            return GuardrailOutput(
                reasoning="Agente não encontrado na configuração",
                is_in_scope=True,  # Permite por padrão se não configurado
                confidence=0.0,
                suggested_action="continue"
            )
        
        prompt = self._build_evaluation_prompt(message, agent_config)
        
        try:
            response = await self.config.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em análise de contexto e escopo de conversas. "
                                 "Avalie se a mensagem do usuário está de acordo com o escopo do agente."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            return self._parse_response(result_text)
            
        except Exception as e:
            return GuardrailOutput(
                reasoning=f"Erro na avaliação: {str(e)}",
                is_in_scope=True,  # Permite por padrão em caso de erro
                confidence=0.0,
                suggested_action="continue"
            )
    
    def _build_evaluation_prompt(self, message: str, agent_config: Dict[str, Any]) -> str:
        """Constrói prompt para avaliação"""
        about = agent_config.get("about", "")
        
        prompt = f"""
Analise se a mensagem do usuário está de acordo com o escopo do agente.

SOBRE O AGENTE:
{about}

MENSAGEM DO USUÁRIO:
"{message}"

INSTRUÇÕES:
1. Analise se a mensagem está relacionada ao escopo do agente descrito acima
2. Considere tanto o que o agente DEVE fazer quanto o que NÃO DEVE fazer
3. Forneça uma pontuação de confiança (0.0 a 1.0)
4. Sugira uma ação: "continue", "redirect", "refuse"

FORMATO DE RESPOSTA:
RAZÃO: [explicação detalhada da análise]
ESCOPO: [true/false]
CONFIANÇA: [0.0-1.0]
AÇÃO: [continue/redirect/refuse]
"""
        return prompt
    
    def _parse_response(self, response_text: str) -> GuardrailOutput:
        """Parseia resposta do modelo"""
        try:
            lines = response_text.strip().split('\n')
            reasoning = ""
            is_in_scope = True
            confidence = 0.5
            suggested_action = "continue"
            
            for line in lines:
                if line.startswith("RAZÃO:"):
                    reasoning = line.replace("RAZÃO:", "").strip()
                elif line.startswith("ESCOPO:"):
                    scope_text = line.replace("ESCOPO:", "").strip().lower()
                    is_in_scope = scope_text == "true"
                elif line.startswith("CONFIANÇA:"):
                    try:
                        confidence = float(line.replace("CONFIANÇA:", "").strip())
                    except ValueError:
                        confidence = 0.5
                elif line.startswith("AÇÃO:"):
                    suggested_action = line.replace("AÇÃO:", "").strip().lower()
            
            return GuardrailOutput(
                reasoning=reasoning or "Análise realizada",
                is_in_scope=is_in_scope,
                confidence=confidence,
                suggested_action=suggested_action
            )
            
        except Exception as e:
            return GuardrailOutput(
                reasoning=f"Erro no parse da resposta: {str(e)}",
                is_in_scope=True,
                confidence=0.0,
                suggested_action="continue"
            )


# Função de conveniência para uso com agentes
def get_guardrails_for_agent(agent_name: str):
    """
    Retorna lista de guardrails para o agente especificado.
    Integra o sistema de guardrails com os agentes OpenAI.
    """
    from agents import input_guardrail, GuardrailFunctionOutput, RunContextWrapper, Agent, TResponseInputItem
    
    @input_guardrail
    async def guardrail_function(
        context: RunContextWrapper, 
        agent: Agent, 
        input: str | list[TResponseInputItem]
    ) -> GuardrailFunctionOutput:
        """
        Função de guardrail que será chamada pelo agente OpenAI.
        Retorna GuardrailFunctionOutput indicando se deve bloquear a mensagem.
        """
        try:
            # Extrair mensagem do input
            if isinstance(input, str):
                message = input
            elif isinstance(input, list) and len(input) > 0:
                # Pegar a última mensagem do usuário
                user_messages = [item for item in input if item.get("role") == "user"]
                if user_messages:
                    message = user_messages[-1].get("content", "")
                else:
                    message = ""
            else:
                message = ""
            
            if not message:
                return GuardrailFunctionOutput(
                    output_info={"reasoning": "Mensagem vazia", "is_in_scope": True},
                    tripwire_triggered=False
                )
            
            # Usar o sistema de guardrails
            guardrail_system = GuardrailSystem()
            result = await guardrail_system.evaluate_message(message, agent_name)
            
            return GuardrailFunctionOutput(
                output_info={
                    "reasoning": result.reasoning,
                    "is_in_scope": result.is_in_scope,
                    "confidence": result.confidence,
                    "suggested_action": result.suggested_action
                },
                tripwire_triggered=not result.is_in_scope
            )
            
        except Exception as e:
            # Em caso de erro, permitir a mensagem (fail-open)
            print(f"Erro no guardrail para {agent_name}: {e}")
            return GuardrailFunctionOutput(
                output_info={"reasoning": f"Erro: {str(e)}", "is_in_scope": True},
                tripwire_triggered=False
            )
    
    return [guardrail_function]


# Função de conveniência para uso direto
async def check_message_scope(
    message: str, 
    agent_name: str, 
    config_path: Optional[str] = None
) -> GuardrailOutput:
    """
    Função de conveniência para verificar escopo de mensagem
    
    Args:
        message: Mensagem do usuário
        agent_name: Nome do agente
        config_path: Caminho opcional para configuração específica
        
    Returns:
        GuardrailOutput com resultado da avaliação
    """
    guardrail_system = GuardrailSystem(config_path)
    return await guardrail_system.evaluate_message(message, agent_name)


# Exemplo de uso
async def main():
    """Exemplo de uso do sistema de guardrails"""
    guardrail_system = GuardrailSystem()
    
    # Teste com diferentes mensagens
    test_messages = [
        "Preciso de ajuda com meu produto",
        "Como resolver 2x + 5 = 11?",
        "Qual é a política de devolução?",
        "Me ajude com programação Python"
    ]
    
    agent_name = "triage_agent"
    
    for message in test_messages:
        print(f"\nMensagem: {message}")
        result = await guardrail_system.evaluate_message(message, agent_name)
        print(f"Escopo: {result.is_in_scope}")
        print(f"Confiança: {result.confidence}")
        print(f"Ação: {result.suggested_action}")
        print(f"Razão: {result.reasoning}")


if __name__ == "__main__":
    asyncio.run(main())
