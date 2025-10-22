#!/usr/bin/env python3
"""
Input Guardrails Genérico para AtendentePro
Sistema de segurança reutilizável que carrega configurações específicas do cliente
"""

import json
import re
import yaml
from typing import Dict, List, Any
from pathlib import Path
from agents import (
    ToolInputGuardrailData,
    ToolGuardrailFunctionOutput,
    tool_input_guardrail,
)


class GuardrailConfig:
    """Carrega configurações de guardrails do template do cliente"""
    
    def __init__(self, client_template_path: str = "Template/White_Martins"):
        self.client_path = Path(__file__).parent / client_template_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo guardrails_config.yaml"""
        config_file = self.client_path / "guardrails_config.yaml"
        
        if not config_file.exists():
            # Configuração padrão se arquivo não existir
            return self._get_default_config()
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão genérica"""
        return {
            "sensitive_words": [
                "password", "senha", "token", "key", "secret",
                "hack", "exploit", "malware", "virus",
            ],
            "off_topic_keywords": [
                "bitcoin", "criptomoeda", "investimento",
                "política", "eleição", "governo",
                "religião", "deus", "jesus",
                "futebol", "esporte", "jogo",
            ],
            "suspicious_patterns": [
                r"delete\s+.*",
                r"drop\s+.*", 
                r"exec\s+.*",
                r"eval\s+.*",
                r"system\s+.*",
            ],
            "valid_codes": [],
            "min_message_length": 3,
            "spam_patterns": [
                r'(.)\1{4,}',  # Repetição excessiva
            ]
        }
    
    def get_sensitive_words(self) -> List[str]:
        """Retorna lista de palavras sensíveis"""
        return self.config.get("sensitive_words", [])
    
    def get_off_topic_keywords(self) -> List[str]:
        """Retorna lista de palavras fora do escopo"""
        return self.config.get("off_topic_keywords", [])
    
    def get_suspicious_patterns(self) -> List[str]:
        """Retorna lista de padrões suspeitos"""
        return self.config.get("suspicious_patterns", [])
    
    def get_valid_codes(self) -> List[str]:
        """Retorna lista de códigos válidos"""
        return self.config.get("valid_codes", [])
    
    def get_topics(self) -> Dict[str, Dict[str, Any]]:
        """Retorna estrutura de tópicos com códigos"""
        return self.config.get("topics", {})
    
    def get_codes_for_topic(self, topic_name: str) -> List[str]:
        """Retorna códigos válidos para um tópico específico"""
        topics = self.get_topics()
        if topic_name in topics:
            return topics[topic_name].get("codes", [])
        return []
    
    def get_all_valid_codes_from_topics(self) -> List[str]:
        """Retorna todos os códigos válidos de todos os tópicos"""
        all_codes = []
        topics = self.get_topics()
        for topic_data in topics.values():
            all_codes.extend(topic_data.get("codes", []))
        return list(set(all_codes))  # Remove duplicatas
    
    def get_min_message_length(self) -> int:
        """Retorna tamanho mínimo de mensagem"""
        return self.config.get("min_message_length", 3)
    
    def get_spam_patterns(self) -> List[str]:
        """Retorna lista de padrões de spam"""
        return self.config.get("spam_patterns", [])


# Instância global da configuração
guardrail_config = GuardrailConfig()


@tool_input_guardrail
def reject_sensitive_content(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """
    Rejeita chamadas de ferramenta que contenham conteúdo sensível.
    Configurações carregadas dinamicamente do template do cliente.
    """
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return ToolGuardrailFunctionOutput(output_info="Argumentos JSON inválidos")

    sensitive_words = guardrail_config.get_sensitive_words()
    suspicious_patterns = guardrail_config.get_suspicious_patterns()

    # Verificar palavras sensíveis
    for key, value in args.items():
        value_str = str(value).lower()
        
        # Verificar palavras sensíveis
        for word in sensitive_words:
            if word.lower() in value_str:
                return ToolGuardrailFunctionOutput.reject_content(
                    message=f"🚨 Chamada de ferramenta bloqueada: contém '{word}'",
                    output_info={
                        "blocked_word": word,
                        "argument": key,
                        "reason": "conteudo_sensivel"
                    },
                )
        
        # Verificar padrões suspeitos
        for pattern in suspicious_patterns:
            if re.search(pattern, value_str, re.IGNORECASE):
                return ToolGuardrailFunctionOutput.reject_content(
                    message=f"🚨 Chamada de ferramenta bloqueada: padrão suspeito detectado",
                    output_info={
                        "blocked_pattern": pattern,
                        "argument": key,
                        "reason": "padrao_suspeito"
                    },
                )

    return ToolGuardrailFunctionOutput(output_info="Entrada validada com sucesso")


@tool_input_guardrail
def reject_off_topic_queries(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """
    Rejeita consultas fora do escopo da aplicação.
    Escopo definido dinamicamente pelo template do cliente.
    """
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return ToolGuardrailFunctionOutput(output_info="Argumentos JSON inválidos")

    off_topic_keywords = guardrail_config.get_off_topic_keywords()

    # Verificar tópicos fora do escopo
    for key, value in args.items():
        value_str = str(value).lower()
        
        for keyword in off_topic_keywords:
            if keyword.lower() in value_str:
                return ToolGuardrailFunctionOutput.reject_content(
                    message=f"🚨 Consulta fora do escopo: '{keyword}' não é relacionado aos serviços da empresa",
                    output_info={
                        "off_topic_keyword": keyword,
                        "argument": key,
                        "reason": "fora_do_escopo",
                        "suggestion": "Por favor, faça perguntas relacionadas aos serviços da empresa."
                    },
                )

    return ToolGuardrailFunctionOutput(output_info="Consulta dentro do escopo válido")


@tool_input_guardrail
def validate_business_codes(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """
    Valida códigos específicos do negócio mencionados nas consultas.
    Códigos válidos definidos dinamicamente pelo template do cliente.
    """
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return ToolGuardrailFunctionOutput(output_info="Argumentos JSON inválidos")

    # Usar códigos dos tópicos se disponível, senão usar lista consolidada
    valid_codes = guardrail_config.get_all_valid_codes_from_topics()
    if not valid_codes:
        valid_codes = guardrail_config.get_valid_codes()
    
    # Se não há códigos configurados, não validar
    if not valid_codes:
        return ToolGuardrailFunctionOutput(output_info="Validação de códigos não configurada")

    for key, value in args.items():
        value_str = str(value)
        
        # Procurar por códigos IVA no texto (padrão específico para IVA)
        code_pattern = r'\b([A-Za-z]\d|[A-Za-z]{2})\b'  # Aceitar maiúsculas e minúsculas
        matches = re.findall(code_pattern, value_str)
        matches = [match.upper() for match in matches]  # Converter para maiúsculas
        
        for match in matches:
            if match not in valid_codes:
                return ToolGuardrailFunctionOutput.reject_content(
                    message=f"🚨 Código IVA inválido: '{match}' não é um código válido",
                    output_info={
                        "invalid_code": match,
                        "argument": key,
                        "reason": "codigo_iva_invalido",
                        "valid_codes_sample": valid_codes[:10]  # Mostrar apenas alguns exemplos
                    },
                )

    return ToolGuardrailFunctionOutput(output_info="Códigos IVA validados")


@tool_input_guardrail
def validate_topic_and_codes(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """
    Valida tópicos e códigos específicos por tópico.
    Validação baseada na estrutura de tópicos do template do cliente.
    """
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return ToolGuardrailFunctionOutput(output_info="Argumentos JSON inválidos")

    topics = guardrail_config.get_topics()
    
    # Se não há tópicos configurados, não validar
    if not topics:
        return ToolGuardrailFunctionOutput(output_info="Validação de tópicos não configurada")

    for key, value in args.items():
        value_str = str(value).lower()
        
        # Procurar por códigos IVA no texto
        code_pattern = r'\b([A-Za-z]\d|[A-Za-z]{2})\b'  # Aceitar maiúsculas e minúsculas
        matches = re.findall(code_pattern, value_str)
        matches = [match.upper() for match in matches]  # Converter para maiúsculas
        
        if matches:
            # Para cada código encontrado, verificar se está no tópico correto
            for code in matches:
                code_found_in_topic = False
                topic_for_code = None
                
                # Encontrar em qual tópico o código está
                for topic_name, topic_data in topics.items():
                    if code in topic_data.get("codes", []):
                        code_found_in_topic = True
                        topic_for_code = topic_name
                        break
                
                if not code_found_in_topic:
                    return ToolGuardrailFunctionOutput.reject_content(
                        message=f"🚨 Código IVA '{code}' não encontrado em nenhum tópico válido",
                        output_info={
                            "invalid_code": code,
                            "argument": key,
                            "reason": "codigo_nao_encontrado_em_topicos",
                            "available_topics": list(topics.keys())
                        },
                    )
                
                # Verificar se o contexto da pergunta corresponde ao tópico do código
                topic_description = topics[topic_for_code].get("description", "").lower()
                
                # Palavras-chave que indicam contexto do tópico
                topic_keywords = {
                    "compra_industrializacao": ["industrialização", "industrial", "produção", "manufaturado"],
                    "compra_comercializacao": ["comercialização", "revenda", "comercial"],
                    "compra_ativo_operacional": ["ativo operacional", "máquina", "equipamento", "cilindro"],
                    "compra_ativo_projeto": ["ativo projeto", "projeto", "andamento"],
                    "consumo_administrativo_ativo_nao_operacional": ["administrativo", "escritório", "limpeza", "ti"],
                    "aquisicao_frete": ["frete", "transporte", "logística"],
                    "aquisicao_energia_eletrica": ["energia", "elétrica", "eletricidade"],
                    "aquisicao_servicos_ligados_a_operacao": ["serviço operação", "manutenção", "assistência", "engenharia"],
                    "aquisicao_servicos_nao_ligados_a_operacao": ["serviço não operação", "consultoria", "auditoria", "inspeção"]
                }
                
                # Verificar se o contexto da pergunta corresponde ao tópico
                context_matches = False
                if topic_for_code in topic_keywords:
                    for keyword in topic_keywords[topic_for_code]:
                        if keyword in value_str:
                            context_matches = True
                            break
                
                if not context_matches:
                    return ToolGuardrailFunctionOutput.reject_content(
                        message=f"🚨 Código IVA '{code}' não corresponde ao contexto da pergunta. Este código é para: {topic_description}",
                        output_info={
                            "code": code,
                            "expected_topic": topic_for_code,
                            "topic_description": topic_description,
                            "argument": key,
                            "reason": "codigo_contexto_incompativel"
                        },
                    )

    return ToolGuardrailFunctionOutput(output_info="Tópicos e códigos validados")


@tool_input_guardrail
def detect_spam_patterns(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """
    Detecta padrões de spam ou mensagens repetitivas.
    Padrões configuráveis pelo template do cliente.
    """
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return ToolGuardrailFunctionOutput(output_info="Argumentos JSON inválidos")

    spam_patterns = guardrail_config.get_spam_patterns()
    min_length = guardrail_config.get_min_message_length()

    for key, value in args.items():
        value_str = str(value)
        
        # Detectar padrões de spam configurados
        for pattern in spam_patterns:
            if re.search(pattern, value_str):
                return ToolGuardrailFunctionOutput.reject_content(
                    message="🚨 Mensagem bloqueada: padrão de spam detectado",
                    output_info={
                        "argument": key,
                        "reason": "padrao_spam",
                        "detected_pattern": pattern
                    },
                )
        
        # Detectar mensagens muito curtas
        if len(value_str.strip()) < min_length:
            return ToolGuardrailFunctionOutput.reject_content(
                message=f"🚨 Mensagem muito curta: forneça mais detalhes (mínimo {min_length} caracteres)",
                output_info={
                    "argument": key,
                    "reason": "mensagem_muito_curta",
                    "min_length": min_length
                },
            )

    return ToolGuardrailFunctionOutput(output_info="Padrões de spam verificados")


# Lista de todos os guardrails disponíveis
AVAILABLE_GUARDRAILS = [
    reject_sensitive_content,
    reject_off_topic_queries,
    validate_business_codes,
    validate_topic_and_codes,
    detect_spam_patterns,
]


def get_guardrails_for_agent(agent_name: str) -> List:
    """
    Retorna os guardrails apropriados para cada agente.
    Configuração carregada dinamicamente do template do cliente.
    """
    # Configuração padrão genérica
    default_guardrails_map = {
        "Triage Agent": [reject_off_topic_queries, detect_spam_patterns],
        "Flow Agent": [reject_off_topic_queries],
        "Interview Agent": [reject_sensitive_content],
        "Answer Agent": [reject_sensitive_content, validate_topic_and_codes],
        "Confirmation Agent": [reject_sensitive_content],
        "Knowledge Agent": [reject_off_topic_queries, detect_spam_patterns],
        "Usage Agent": [detect_spam_patterns],
    }
    
    # Tentar carregar configuração específica do cliente
    try:
        client_config_file = guardrail_config.client_path / "agent_guardrails_config.yaml"
        if client_config_file.exists():
            with open(client_config_file, 'r', encoding='utf-8') as f:
                client_config = yaml.safe_load(f)
                return client_config.get(agent_name, default_guardrails_map.get(agent_name, [reject_sensitive_content]))
    except Exception:
        pass  # Usar configuração padrão se houver erro
    
    return default_guardrails_map.get(agent_name, [reject_sensitive_content])


def reload_config():
    """Recarrega configurações do template do cliente"""
    global guardrail_config
    guardrail_config = GuardrailConfig()


if __name__ == "__main__":
    print("🛡️ Input Guardrails Genérico para AtendentePro")
    print(f"Configuração carregada de: {guardrail_config.client_path}")
    print(f"Guardrails disponíveis: {len(AVAILABLE_GUARDRAILS)}")
    print("✅ Sistema de segurança ativo e configurável")