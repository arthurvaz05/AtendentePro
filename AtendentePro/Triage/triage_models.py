from __future__ import annotations
import os
import yaml
from typing import Dict, Any, Optional

# Este arquivo foi simplificado após a remoção do sistema de keywords
# Sistema de triage simplificado

# Mantido apenas para compatibilidade com imports existentes
triage_keywords_map = {}
triage_keywords_text = ""

def format_triage_keywords() -> str:
    """Função mantida para compatibilidade, retorna string vazia"""
    return ""

# Funções para carregar configurações dinamicamente
def load_triage_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Carrega configuração do triage_config.yaml"""
    if config_path is None:
        # Procura primeiro na pasta Template do cliente atual
        template_paths = [
            "AtendentePro/Template/White_Martins/triage_config.yaml",
            "AtendentePro/Template/standard/triage_config.yaml",
            "triage_config.yaml"
        ]
        
        for path in template_paths:
            if os.path.exists(path):
                config_path = path
                break
        
        if config_path is None:
            return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {}

def load_guardrail_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Carrega configuração do guardrails_config.yaml"""
    if config_path is None:
        # Procura primeiro na pasta Template do cliente atual
        template_paths = [
            "AtendentePro/Template/White_Martins/guardrails_config.yaml",
            "AtendentePro/Template/standard/guardrails_config.yaml",
            "guardrails_config.yaml"
        ]
        
        for path in template_paths:
            if os.path.exists(path):
                config_path = path
                break
        
        if config_path is None:
            return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {}

def get_triage_about_template() -> str:
    """Obtém o template 'about' do triage_agent do guardrails_config.yaml"""
    config = load_guardrail_config()
    triage_about = config.get('agent_scopes', {}).get('triage_agent', {}).get('about', '')
    
    if not triage_about:
        return "Sistema de triage genérico"
    
    return triage_about.strip()

def get_triage_keywords() -> Dict[str, Any]:
    """Obtém as keywords do triage_config.yaml"""
    config = load_triage_config()
    return config.get('agent_keywords', {})

def get_routing_rules() -> Dict[str, Any]:
    """Obtém as regras de roteamento do triage_config.yaml"""
    config = load_triage_config()
    return config.get('routing_rules', {})

def build_route_module() -> str:
    """Constrói o módulo ROUTE dinamicamente usando keywords e regras do triage_config.yaml"""
    agent_keywords = get_triage_keywords()
    routing_rules = get_routing_rules()
    
    # Construir lista de agentes e suas keywords
    agents_info = []
    for agent_name, agent_config in agent_keywords.items():
        keywords = agent_config.get('keywords', [])
        description = agent_config.get('description', '')
        keywords_str = ', '.join(keywords[:5])  # Mostrar apenas as primeiras 5 keywords
        if len(keywords) > 5:
            keywords_str += f" (e mais {len(keywords) - 5} keywords)"
        
        agents_info.append(f"    - {agent_name.upper()}: {keywords_str}")
        agents_info.append(f"      Descrição: {description}")
    
    # Construir regras de prioridade
    priority_order = routing_rules.get('priority_order', [])
    priority_str = ' -> '.join([f"{agent.upper()}" for agent in priority_order])
    
    # Agente padrão
    default_agent = routing_rules.get('default_agent', 'knowledge_agent')
    
    return f"""
    [ROUTE]
    - (Raciocínio interno) Com base na análise das keywords do triage_config.yaml e contexto da mensagem:
    
    KEYWORDS POR AGENTE (carregadas dinamicamente do triage_config.yaml):
{chr(10).join(agents_info)}
    
    REGRAS DE ROTEAMENTO:
    - Prioridade: {priority_str}
    - Agente padrão: {default_agent.upper()}
    
    1. Se identificar keywords de múltiplos agentes:
       - Use a prioridade definida acima
       - Escolha o agente com maior relevância para a pergunta específica
       - Considere o contexto e a intenção do usuário
    
    2. Se não identificar keywords claras:
       - Direcione para o {default_agent.upper()} (agente padrão)
       - Ou para USAGE_AGENT se for sobre uso do sistema
    
    3. Sempre considere o contexto da conversa e necessidades específicas do cliente
    
    4. Para mensagens fora do escopo, use o sistema de guardrails (módulo ANALYZE)
"""

__all__ = [
    "triage_keywords_map",
    "triage_keywords_text", 
    "format_triage_keywords",
    "load_triage_config",
    "load_guardrail_config",
    "get_triage_about_template",
    "get_triage_keywords",
    "get_routing_rules",
    "build_route_module",
]