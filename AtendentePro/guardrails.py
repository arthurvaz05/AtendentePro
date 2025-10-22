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

    valid_codes = guardrail_config.get_valid_codes()
    
    # Se não há códigos configurados, não validar
    if not valid_codes:
        return ToolGuardrailFunctionOutput(output_info="Validação de códigos não configurada")

    for key, value in args.items():
        value_str = str(value)
        
        # Procurar por códigos no texto (padrão genérico)
        code_pattern = r'\b(\d{2,})\b'  # Códigos de 2 ou mais dígitos
        matches = re.findall(code_pattern, value_str)
        
        for match in matches:
            if match not in valid_codes:
                return ToolGuardrailFunctionOutput.reject_content(
                    message=f"🚨 Código inválido: '{match}' não é um código válido",
                    output_info={
                        "invalid_code": match,
                        "argument": key,
                        "reason": "codigo_invalido",
                        "valid_codes": valid_codes[:10]  # Mostrar apenas alguns exemplos
                    },
                )

    return ToolGuardrailFunctionOutput(output_info="Códigos validados")


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
        "Flow Agent": [reject_off_topic_queries, validate_business_codes],
        "Interview Agent": [reject_sensitive_content, validate_business_codes],
        "Answer Agent": [reject_sensitive_content, validate_business_codes],
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