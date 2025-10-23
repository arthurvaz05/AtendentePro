#!/usr/bin/env python3
"""
Input Guardrails Especializados com IA
Sistema ultra-simplificado que usa apenas descrições de agentes
Toda validação é feita pela IA baseada na descrição do agente
"""

import json
import yaml
from typing import Dict, List, Any
from pathlib import Path
from agents import (
    ToolInputGuardrailData,
    ToolGuardrailFunctionOutput,
    tool_input_guardrail,
)
from openai import OpenAI
import os


class GuardrailConfig:
    """Carrega apenas descrições de agentes do template do cliente"""
    
    def __init__(self, client_template_path: str = "Template/White_Martins"):
        self.client_path = Path(__file__).parent / client_template_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega apenas descrições de agentes"""
        config_file = self.client_path / "guardrails_config.yaml"
        
        if not config_file.exists():
            return self._get_default_config()
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão genérica"""
        return {
            "agent_scope_descriptions": {
                "Triage Agent": {
                    "description": "Agente de triagem que roteia conversas para agentes especializados"
                },
                "Flow Agent": {
                    "description": "Agente de fluxo que identifica tópicos específicos"
                },
                "Interview Agent": {
                    "description": "Agente de entrevista que coleta informações detalhadas"
                },
                "Answer Agent": {
                    "description": "Agente de resposta que fornece informações e soluções"
                },
                "Confirmation Agent": {
                    "description": "Agente de confirmação que valida informações"
                },
                "Knowledge Agent": {
                    "description": "Agente de conhecimento que consulta documentação"
                },
                "Usage Agent": {
                    "description": "Agente de uso que explica funcionalidades do sistema"
                }
            }
        }
    
    def get_agent_description(self, agent_name: str) -> str:
        """Retorna apenas a descrição do agente"""
        descriptions = self.config.get("agent_scope_descriptions", {})
        if agent_name in descriptions:
            return descriptions[agent_name].get("description", "")
        return ""
    
    def get_agent_scope(self, agent_name: str) -> str:
        """Retorna o escopo específico de um agente"""
        descriptions = self.config.get("agent_scope_descriptions", {})
        if agent_name in descriptions:
            return descriptions[agent_name].get("scope", "")
        return ""
    
    def get_topics(self) -> Dict[str, Dict[str, Any]]:
        """Retorna a estrutura de tópicos e códigos"""
        return self.config.get("topics", {})


# Instância global da configuração
guardrail_config = GuardrailConfig()

# Cliente OpenAI para avaliação de conteúdo
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))


def evaluate_content_with_ai(user_message: str, agent_name: str, agent_description: str, agent_scope: str, topics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Usa IA para avaliar se o conteúdo da mensagem é permitido para o agente.
    Avalia TUDO baseado na descrição, escopo e tópicos do agente.
    
    Args:
        user_message: Mensagem do usuário
        agent_name: Nome do agente
        agent_description: Descrição completa do agente
        agent_scope: Escopo específico do agente
        topics: Estrutura de tópicos e códigos válidos
    
    Returns:
        Dict com resultado da avaliação
    """
    
    # Preparar informações sobre tópicos para a IA
    topics_info = ""
    if topics:
        topics_info = "\n\nTÓPICOS E CÓDIGOS VÁLIDOS:\n"
        for topic_key, topic_data in topics.items():
            topic_desc = topic_data.get("description", "")
            codes = topic_data.get("codes", [])
            topics_info += f"- {topic_desc}: {', '.join(codes)}\n"
    
    prompt = f"""
Você é um especialista em análise de conteúdo para sistemas de atendimento empresarial.

TAREFA: Avaliar se a mensagem do usuário é permitida para o agente específico.

AGENTE: {agent_name}
DESCRIÇÃO: {agent_description}
ESCOPO: {agent_scope}
{topics_info}

MENSAGEM DO USUÁRIO: "{user_message}"

INSTRUÇÕES:
1. Analise se a mensagem está relacionada à descrição e escopo do agente
2. Verifique se contém conteúdo sensível (senhas, hacking, fraudes, palavrões, informações pessoais)
3. Detecte padrões de spam ou mensagens muito curtas
4. Valide códigos específicos mencionados (se houver) usando os tópicos fornecidos
5. Considere o contexto empresarial e domínio de negócio
6. Seja rigoroso mas justo na avaliação
7. Responda APENAS com JSON válido

CRITÉRIOS DE AVALIAÇÃO:
- ✅ APROVADO: Mensagem válida, dentro do escopo da descrição, sem conteúdo sensível
- ❌ REJEITADO: Mensagem fora do escopo, conteúdo sensível, spam, ou códigos inválidos

RESPOSTA (JSON):
{{
    "approved": true/false,
    "reason": "explicação breve da decisão",
    "confidence": 0.0-1.0,
    "category": "escopo|conteudo_sensivel|spam|codigo_invalido|outro",
    "suggested_action": "ação sugerida se rejeitado"
}}
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de conteúdo empresarial. Responda APENAS com JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Tentar extrair JSON da resposta
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # Se não conseguir fazer parse do JSON, tentar extrair manualmente
            if "approved" in result_text.lower() and "true" in result_text.lower():
                result = {"approved": True, "reason": "Aprovado por IA", "confidence": 0.8, "category": "aprovado"}
            elif "approved" in result_text.lower() and "false" in result_text.lower():
                result = {"approved": False, "reason": "Rejeitado por IA", "confidence": 0.8, "category": "rejeitado"}
            else:
                result = {"approved": True, "reason": "Falha na análise - permitindo", "confidence": 0.5, "category": "fallback"}
        
        return result
        
    except Exception as e:
        # Em caso de erro, permitir (fail-safe)
        return {
            "approved": True,
            "reason": f"Erro na avaliação IA: {str(e)} - permitindo por segurança",
            "confidence": 0.3,
            "category": "erro"
        }


@tool_input_guardrail
def validate_content_with_ai(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """
    Valida todo o conteúdo da mensagem usando IA.
    Usa apenas a descrição do agente para fazer toda a análise.
    """
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return ToolGuardrailFunctionOutput(output_info="Argumentos JSON inválidos")

    # Obter o nome do agente atual (se disponível no contexto)
    agent_name = getattr(data.context, 'agent_name', 'Triage Agent')
    
    # Obter descrição, escopo e tópicos do agente
    agent_description = guardrail_config.get_agent_description(agent_name)
    agent_scope = guardrail_config.get_agent_scope(agent_name)
    topics = guardrail_config.get_topics()
    
    if not agent_description:
        # Se não há descrição definida, permitir (fallback)
        return ToolGuardrailFunctionOutput(output_info="Descrição não definida - permitindo")

    # Extrair mensagem do usuário dos argumentos
    user_message = ""
    for key, value in args.items():
        if isinstance(value, str) and len(value.strip()) > 0:
            user_message = value.strip()
            break
    
    if not user_message:
        return ToolGuardrailFunctionOutput(output_info="Mensagem vazia - permitindo")

    # Usar IA para avaliar todo o conteúdo baseado na descrição, escopo e tópicos
    ai_evaluation = evaluate_content_with_ai(user_message, agent_name, agent_description, agent_scope, topics)
    
    if not ai_evaluation.get("approved", True):
        # IA rejeitou a mensagem
        reason = ai_evaluation.get("reason", "Conteúdo não permitido")
        confidence = ai_evaluation.get("confidence", 0.8)
        category = ai_evaluation.get("category", "outro")
        suggested_action = ai_evaluation.get("suggested_action", f"Faça perguntas relacionadas ao escopo do {agent_name}")
        
        return ToolGuardrailFunctionOutput.reject_content(
            message=f"🚨 Mensagem bloqueada pelo {agent_name}: {reason}",
            output_info={
                "user_message": user_message,
                "agent_name": agent_name,
                "agent_description": agent_description,
                "agent_scope": agent_scope,
                "topics_available": list(topics.keys()) if topics else [],
                "ai_reason": reason,
                "ai_confidence": confidence,
                "ai_category": category,
                "suggested_action": suggested_action,
                "reason": f"conteudo_nao_permitido_{category}",
                "suggestion": suggested_action
            },
        )
    
    # IA aprovou a mensagem
    reason = ai_evaluation.get("reason", "Conteúdo aprovado")
    confidence = ai_evaluation.get("confidence", 0.8)
    category = ai_evaluation.get("category", "aprovado")
    
    return ToolGuardrailFunctionOutput(
        output_info=f"Mensagem aprovada pelo {agent_name}: {reason} (confiança: {confidence:.2f}, categoria: {category})"
    )


# Lista de todos os guardrails disponíveis - APENAS IA
AVAILABLE_GUARDRAILS = [
    validate_content_with_ai,  # Única função de validação com IA
]


def get_guardrails_for_agent(agent_name: str) -> List:
    """
    Retorna os guardrails apropriados para cada agente.
    Configuração carregada dinamicamente do template do cliente.
    """
    # Configuração padrão genérica - apenas IA
    default_guardrails_map = {
        "Triage Agent": [validate_content_with_ai],
        "Flow Agent": [validate_content_with_ai],
        "Interview Agent": [validate_content_with_ai],
        "Answer Agent": [validate_content_with_ai],
        "Confirmation Agent": [validate_content_with_ai],
        "Knowledge Agent": [validate_content_with_ai],
        "Usage Agent": [validate_content_with_ai],
    }
    
    # Tentar carregar configuração específica do cliente
    try:
        client_config_file = guardrail_config.client_path / "agent_guardrails_config.yaml"
        if client_config_file.exists():
            with open(client_config_file, 'r', encoding='utf-8') as f:
                client_config = yaml.safe_load(f)
                return client_config.get(agent_name, default_guardrails_map.get(agent_name, [validate_content_with_ai]))
    except Exception:
        pass  # Usar configuração padrão se houver erro
    
    return default_guardrails_map.get(agent_name, [validate_content_with_ai])


def reload_config():
    """Recarrega configurações do template do cliente"""
    global guardrail_config
    guardrail_config = GuardrailConfig()


if __name__ == "__main__":
    print("🤖 Input Guardrails Especializados com IA")
    print(f"Configuração carregada de: {guardrail_config.client_path}")
    print(f"Guardrails disponíveis: {len(AVAILABLE_GUARDRAILS)}")
    print("✅ Sistema especializado usando descrições, escopos e tópicos de agentes")