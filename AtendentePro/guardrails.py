#!/usr/bin/env python3
"""
Input Guardrails para AtendentePro
Sistema de segurança que monitora entradas em tempo real
"""

import json
import re
from typing import Dict, List, Any
from agents import (
    ToolInputGuardrailData,
    ToolGuardrailFunctionOutput,
    tool_input_guardrail,
)

# Palavras sensíveis específicas do domínio AtendentePro
SENSITIVE_WORDS = [
    # Segurança
    "password", "senha", "token", "key", "secret",
    "hack", "exploit", "malware", "virus",
    
    # Domínio específico - IVA/Energia
    "fraude", "sonegação", "evasão", "ilegal",
    "manipulação", "corrupção", "suborno",
    
    # Palavras ofensivas
    "idiota", "burro", "estúpido", "imbecil",
    "merda", "porra", "caralho", "foda",
]

# Padrões suspeitos
SUSPICIOUS_PATTERNS = [
    r"delete\s+.*",  # Comandos de exclusão
    r"drop\s+.*",    # Comandos SQL perigosos
    r"exec\s+.*",    # Execução de código
    r"eval\s+.*",    # Avaliação de código
    r"system\s+.*",  # Chamadas de sistema
]

# Tópicos fora do escopo
OFF_TOPIC_KEYWORDS = [
    "bitcoin", "criptomoeda", "investimento",
    "política", "eleição", "governo",
    "religião", "deus", "jesus",
    "futebol", "esporte", "jogo",
    "receita", "cocina", "comida",
]

@tool_input_guardrail
def reject_sensitive_content(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """
    Rejeita chamadas de ferramenta que contenham conteúdo sensível.
    Específico para o domínio AtendentePro (IVA, energia elétrica).
    """
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return ToolGuardrailFunctionOutput(output_info="Argumentos JSON inválidos")

    # Verificar palavras sensíveis
    for key, value in args.items():
        value_str = str(value).lower()
        
        # Verificar palavras sensíveis
        for word in SENSITIVE_WORDS:
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
        for pattern in SUSPICIOUS_PATTERNS:
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
    Rejeita consultas fora do escopo do AtendentePro.
    Foca em IVA, energia elétrica e temas relacionados.
    """
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return ToolGuardrailFunctionOutput(output_info="Argumentos JSON inválidos")

    # Verificar tópicos fora do escopo
    for key, value in args.items():
        value_str = str(value).lower()
        
        for keyword in OFF_TOPIC_KEYWORDS:
            if keyword.lower() in value_str:
                return ToolGuardrailFunctionOutput.reject_content(
                    message=f"🚨 Consulta fora do escopo: '{keyword}' não é relacionado a IVA/energia",
                    output_info={
                        "off_topic_keyword": keyword,
                        "argument": key,
                        "reason": "fora_do_escopo",
                        "suggestion": "Por favor, faça perguntas relacionadas a IVA, energia elétrica ou serviços da empresa."
                    },
                )

    return ToolGuardrailFunctionOutput(output_info="Consulta dentro do escopo válido")

@tool_input_guardrail
def validate_iva_codes(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """
    Valida códigos IVA mencionados nas consultas.
    Verifica se são códigos válidos do sistema.
    """
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return ToolGuardrailFunctionOutput(output_info="Argumentos JSON inválidos")

    # Códigos IVA válidos (exemplo - ajustar conforme necessário)
    VALID_IVA_CODES = [
        "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
        "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
        "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
    ]

    for key, value in args.items():
        value_str = str(value)
        
        # Procurar por códigos IVA no texto
        iva_pattern = r'\b(\d{2})\b'
        matches = re.findall(iva_pattern, value_str)
        
        for match in matches:
            if match not in VALID_IVA_CODES:
                return ToolGuardrailFunctionOutput.reject_content(
                    message=f"🚨 Código IVA inválido: '{match}' não é um código válido",
                    output_info={
                        "invalid_code": match,
                        "argument": key,
                        "reason": "codigo_iva_invalido",
                        "valid_codes": VALID_IVA_CODES[:10]  # Mostrar apenas alguns exemplos
                    },
                )

    return ToolGuardrailFunctionOutput(output_info="Códigos IVA validados")

@tool_input_guardrail
def detect_spam_patterns(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """
    Detecta padrões de spam ou mensagens repetitivas.
    """
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return ToolGuardrailFunctionOutput(output_info="Argumentos JSON inválidos")

    for key, value in args.items():
        value_str = str(value)
        
        # Detectar repetição excessiva de caracteres
        if re.search(r'(.)\1{4,}', value_str):
            return ToolGuardrailFunctionOutput.reject_content(
                message="🚨 Mensagem bloqueada: padrão de spam detectado",
                output_info={
                    "argument": key,
                    "reason": "padrao_spam",
                    "detected_pattern": "repeticao_excessiva"
                },
            )
        
        # Detectar mensagens muito curtas (possível spam)
        if len(value_str.strip()) < 3:
            return ToolGuardrailFunctionOutput.reject_content(
                message="🚨 Mensagem muito curta: forneça mais detalhes",
                output_info={
                    "argument": key,
                    "reason": "mensagem_muito_curta",
                    "min_length": 3
                },
            )

    return ToolGuardrailFunctionOutput(output_info="Padrões de spam verificados")

# Lista de todos os guardrails disponíveis
AVAILABLE_GUARDRAILS = [
    reject_sensitive_content,
    reject_off_topic_queries,
    validate_iva_codes,
    detect_spam_patterns,
]

def get_guardrails_for_agent(agent_name: str) -> List:
    """
    Retorna os guardrails apropriados para cada agente.
    """
    guardrails_map = {
        "Triage Agent": [reject_off_topic_queries, detect_spam_patterns],
        "Flow Agent": [reject_off_topic_queries, validate_iva_codes],
        "Interview Agent": [reject_sensitive_content, validate_iva_codes],
        "Answer Agent": [reject_sensitive_content, validate_iva_codes],
        "Confirmation Agent": [reject_sensitive_content],
        "Knowledge Agent": [reject_off_topic_queries, detect_spam_patterns],
        "Usage Agent": [detect_spam_patterns],
    }
    
    return guardrails_map.get(agent_name, [reject_sensitive_content])

if __name__ == "__main__":
    print("🛡️ Input Guardrails para AtendentePro")
    print(f"Guardrails disponíveis: {len(AVAILABLE_GUARDRAILS)}")
    print("✅ Sistema de segurança ativo")
