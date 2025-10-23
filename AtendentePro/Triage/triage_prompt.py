
try:
    from .triage_models import (
        get_triage_about_template,
        get_triage_keywords,
        get_routing_rules,
        build_route_module
    )
except ImportError:
    # Fallback para execução direta
    from triage_models import (
        get_triage_about_template,
        get_triage_keywords,
        get_routing_rules,
        build_route_module
    )

def build_intro() -> str:
    """Constrói o INTRO dinamicamente baseado na configuração"""
    triage_about = get_triage_about_template()
    
    return f"""
    Você é um agente de triagem prestativo especializado em análise e roteamento de consultas. 
    Analise a mensagem do usuário, verifique se a pergunta está dentro do escopo de atuação do sistema de agentes, 
    e direcione-a para o agente mais adequado. 
    Considere o contexto da conversa e as necessidades específicas do cliente para fazer o roteamento correto.
    
    SOBRE O TRIAGE AGENT:
    {triage_about}
"""

INTRO = build_intro()

MODULES = """
    Deve seguir as seguintes etapas de forma sequencial (todas são raciocínio interno; não exponha nada ao usuário):
    [READ] - [SUMMARY] - [EXTRACT] - [ANALYZE] - [ROUTE]
"""

READ = """
    [READ]
    - (Raciocínio interno) Leia cuidadosamente a mensagem do usuário.
"""

SUMMARY = """
    [SUMMARY]
    - (Raciocínio interno) Faça um resumo da mensagem do usuário.
"""

EXTRACT = """
    [EXTRACT]
    - (Raciocínio interno) Extraia as informações relevantes da mensagem do usuário.
"""

def build_analyze_module() -> str:
    """Constrói o módulo ANALYZE dinamicamente usando o template do guardrail"""
    triage_about = get_triage_about_template()
    
    return f"""
    [ANALYZE]
    - (Raciocínio interno) Verifique se a pergunta está dentro do escopo de atuação do sistema de agentes.
    
    TEMPLATE DE ANÁLISE (carregado dinamicamente do guardrails_config.yaml):
    
    SOBRE O TRIAGE AGENT:
    {triage_about}
    
    ROLLBACK - Se a mensagem estiver FORA DO ESCOPO:
    - Identifique claramente que a pergunta não está relacionada ao escopo do sistema
    - Explique educadamente que o sistema é especializado no domínio configurado
    - Sugira buscar informações em fontes apropriadas para o tema da pergunta
    - Mantenha o foco nos serviços oferecidos pelo sistema
"""

ANALYZE = build_analyze_module()

ROUTE = build_route_module()


def build_triage_prompts() -> str:
    """Constrói o prompt completo do triage dinamicamente"""
    return (
        INTRO + "\n" + MODULES + "\n" + READ + "\n" + SUMMARY + "\n" + 
        EXTRACT + "\n" + ANALYZE + "\n" + ROUTE
    )

# Prompt principal construído dinamicamente
triage_prompts_agent = build_triage_prompts()

if __name__ == "__main__":
    print(triage_prompts_agent)