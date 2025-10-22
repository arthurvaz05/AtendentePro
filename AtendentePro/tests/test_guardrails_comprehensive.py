#!/usr/bin/env python3
"""
Teste Abrangente dos Guardrails - Cenários Reais
Testa todos os tipos de validação: códigos errados, códigos inexistentes, temas aleatórios
"""

import json
import re
import yaml
from unittest.mock import Mock
from pathlib import Path

# Simular a classe GuardrailConfig para teste
class TestGuardrailConfig:
    """Configuração de teste para guardrails com tópicos"""
    
    def __init__(self):
        self.config = self._load_test_config()
    
    def _load_test_config(self):
        """Carrega configuração de teste com tópicos"""
        return {
            "topics": {
                "compra_industrializacao": {
                    "description": "Compra para industrialização — material manufaturado ou processo produtivo",
                    "codes": ["I0", "ID", "IE", "I8", "I5", "I9", "I2", "I7", "I1", "I3", "I4"]
                },
                "compra_comercializacao": {
                    "description": "Compra para comercialização — produto para revenda sem alteração",
                    "codes": ["R0", "ID", "R6", "R1", "R5", "R3", "R2", "R4"]
                },
                "aquisicao_energia_eletrica": {
                    "description": "Aquisição de energia elétrica — produtiva vs administrativa",
                    "codes": ["E1", "E2", "E3", "E4", "E0"]
                },
                "aquisicao_frete": {
                    "description": "Aquisição de frete — serviços de transporte",
                    "codes": ["F0", "F1", "F5", "FE", "FA", "F2", "FC", "F7", "F3", "FD", "FB", "F4"]
                }
            },
            "on_topic_keywords": [
                "iva", "código", "códigos", "tributário", "tributação", "imposto", "impostos",
                "fiscal", "fiscalização", "nota fiscal", "nf", "nfe", "nfce", "icms", "ipi",
                "pis", "cofins", "simples nacional", "microempresa", "substituição tributária",
                "compra", "compras", "industrialização", "industrial", "produção", "manufaturado",
                "comercialização", "comercial", "revenda", "ativo operacional", "ativo projeto",
                "máquina", "equipamento", "cilindro", "consumo administrativo", "administrativo",
                "escritório", "limpeza", "ti", "frete", "transporte", "logística",
                "energia elétrica", "energia", "elétrica", "eletricidade", "serviço operação",
                "serviço não operação", "manutenção", "assistência", "engenharia", "consultoria",
                "auditoria", "inspeção", "fornecedor", "fornecedores", "cliente", "clientes",
                "empresa", "empresas", "cnpj", "cpf", "pessoa física", "pessoa jurídica",
                "processo", "procedimento", "documentação", "documento", "documentos",
                "análise", "análises", "consulta", "consultas", "orientação", "orientações",
                "suporte", "atendimento", "assistência", "ajuda", "white martins", "white",
                "martins", "gás", "gases", "oxigênio", "nitrogênio", "argônio", "hidrogênio",
                "hélio", "acetileno", "co2", "dióxido de carbono", "soldagem", "corte",
                "laboratório", "hospitalar", "alimentício", "bebida", "refrigeração",
                "ar condicionado", "caldeira", "forno", "queima", "combustão"
            ],
            "sensitive_words": [
                "password", "senha", "token", "key", "secret",
                "hack", "exploit", "malware", "virus",
                "fraude", "sonegação", "evasão", "ilegal"
            ]
        }
    
    def get_topics(self):
        return self.config.get("topics", {})
    
    def get_on_topic_keywords(self):
        return self.config.get("on_topic_keywords", [])
    
    def get_sensitive_words(self):
        return self.config.get("sensitive_words", [])

# Instância de teste
test_config = TestGuardrailConfig()

def reject_off_topic_queries(data):
    """Rejeita consultas fora do escopo usando nova lógica on_topic_keywords"""
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return Mock(output_info="Argumentos JSON inválidos")

    on_topic_keywords = test_config.get_on_topic_keywords()

    # Se não há palavras-chave permitidas configuradas, não validar
    if not on_topic_keywords:
        return Mock(output_info="Validação de tópicos não configurada")

    # Verificar se a consulta contém pelo menos uma palavra-chave permitida
    for key, value in args.items():
        value_str = str(value).lower()
        
        # Verificar se pelo menos uma palavra-chave permitida está presente
        topic_found = False
        for keyword in on_topic_keywords:
            if keyword.lower() in value_str:
                topic_found = True
                break
        
        # Se nenhuma palavra-chave permitida foi encontrada, rejeitar
        if not topic_found:
            return Mock(
                output_info=None,
                message=f"🚨 Consulta fora do escopo: não foi identificado nenhum tópico relacionado aos serviços da empresa"
            )

    return Mock(output_info="Consulta dentro do escopo")

def validate_topic_and_codes(data):
    """Valida tópicos e códigos específicos por tópico"""
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return Mock(output_info="Argumentos JSON inválidos")

    topics = test_config.get_topics()
    
    if not topics:
        return Mock(output_info="Validação de tópicos não configurada")

    for key, value in args.items():
        value_str = str(value)  # Manter maiúsculas para o regex
        value_str_lower = value_str.lower()  # Minúsculas para contexto
        
        # Procurar por códigos IVA no texto (padrão específico para IVA)
        # Capturar códigos como E1, I0, R1, F0, Z9, XX, ABC, etc.
        code_pattern = r'\b([A-Z]\d|[A-Z]{2,3}|\d{2,3})\b'
        matches = re.findall(code_pattern, value_str)
        
        # Filtrar palavras comuns que não são códigos IVA
        common_words = {"QUAL", "PARA", "COM", "SEM", "DOS", "DAS", "DO", "DA", "DE", "EM", "NA", "NO", "IVA", "CODIGO"}
        matches = [match.upper() for match in matches if match.upper() not in common_words]
        
        # Debug: mostrar códigos encontrados
        if matches:
            print(f"    DEBUG: Códigos encontrados: {matches}")
        
        if matches:
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
                    return Mock(
                        output_info=None,
                        message=f"🚨 Código IVA '{code}' não encontrado em nenhum tópico válido"
                    )
                
                # Verificar contexto
                topic_keywords = {
                    "compra_industrializacao": ["industrialização", "industrial", "produção", "manufaturado"],
                    "compra_comercializacao": ["comercialização", "revenda", "comercial"],
                    "aquisicao_energia_eletrica": ["energia", "elétrica", "eletricidade"],
                    "aquisicao_frete": ["frete", "transporte", "logística"]
                }
                
                context_matches = False
                if topic_for_code in topic_keywords:
                    for keyword in topic_keywords[topic_for_code]:
                        if keyword in value_str_lower:
                            context_matches = True
                            break
                
                if not context_matches:
                    topic_description = topics[topic_for_code].get("description", "")
                    return Mock(
                        output_info=None,
                        message=f"🚨 Código IVA '{code}' não corresponde ao contexto da pergunta. Este código é para: {topic_description}"
                    )

    return Mock(output_info="Tópicos e códigos validados")

def reject_sensitive_content(data):
    """Rejeita conteúdo sensível"""
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return Mock(output_info="Argumentos JSON inválidos")

    sensitive_words = test_config.get_sensitive_words()

    for key, value in args.items():
        value_str = str(value).lower()
        
        for word in sensitive_words:
            if word.lower() in value_str:
                return Mock(
                    output_info=None,
                    message=f"🚨 Conteúdo sensível detectado: '{word}'. Sua consulta foi bloqueada."
                )

    return Mock(output_info="Conteúdo validado")

def test_code_wrong_for_topic():
    """Testa códigos corretos mas para tópico errado"""
    
    print("🧪 TESTE: Código Correto para Tópico Errado")
    print("=" * 60)
    
    test_cases = [
        {
            "query": "Qual o código IVA E1 para industrialização?",
            "expected": "bloqueado",
            "reason": "E1 é para energia elétrica, não industrialização"
        },
        {
            "query": "Qual o código IVA I0 para frete?",
            "expected": "bloqueado", 
            "reason": "I0 é para industrialização, não frete"
        },
        {
            "query": "Qual o código IVA R1 para energia elétrica?",
            "expected": "bloqueado",
            "reason": "R1 é para comercialização, não energia"
        },
        {
            "query": "Qual o código IVA F0 para comercialização?",
            "expected": "bloqueado",
            "reason": "F0 é para frete, não comercialização"
        }
    ]
    
    blocked_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n   Teste {i}: {case['query']}")
        print(f"   Esperado: {case['expected']}")
        print(f"   Motivo: {case['reason']}")
        
        # Simular dados
        args = f'{{"query": "{case["query"]}"}}'
        mock_data = Mock()
        mock_data.context = Mock()
        mock_data.context.tool_arguments = args
        
        # Testar guardrail
        result = validate_topic_and_codes(mock_data)
        
        if result.output_info is None:
            print(f"   ✅ BLOQUEADO: {result.message}")
            blocked_count += 1
        else:
            print(f"   ❌ PERMITIDO: {result.output_info}")
    
    print(f"\n📊 Resultado: {blocked_count}/{len(test_cases)} casos bloqueados")
    return blocked_count == len(test_cases)

def test_nonexistent_codes():
    """Testa códigos que não existem"""
    
    print("\n🧪 TESTE: Códigos Inexistentes")
    print("=" * 60)
    
    test_cases = [
        {
            "query": "Qual o código IVA Z9 para energia elétrica?",
            "expected": "bloqueado",
            "reason": "Z9 não existe"
        },
        {
            "query": "Qual o código IVA XX para industrialização?",
            "expected": "bloqueado",
            "reason": "XX não existe"
        },
        {
            "query": "Qual o código IVA 99 para frete?",
            "expected": "bloqueado",
            "reason": "99 não é formato IVA válido"
        },
        {
            "query": "Qual o código IVA ABC para comercialização?",
            "expected": "bloqueado",
            "reason": "ABC não existe"
        }
    ]
    
    blocked_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n   Teste {i}: {case['query']}")
        print(f"   Esperado: {case['expected']}")
        print(f"   Motivo: {case['reason']}")
        
        # Simular dados
        args = f'{{"query": "{case["query"]}"}}'
        mock_data = Mock()
        mock_data.context = Mock()
        mock_data.context.tool_arguments = args
        
        # Testar guardrail
        result = validate_topic_and_codes(mock_data)
        
        if result.output_info is None:
            print(f"   ✅ BLOQUEADO: {result.message}")
            blocked_count += 1
        else:
            print(f"   ❌ PERMITIDO: {result.output_info}")
    
    print(f"\n📊 Resultado: {blocked_count}/{len(test_cases)} casos bloqueados")
    return blocked_count == len(test_cases)

def test_random_topics():
    """Testa temas aleatórios fora do contexto"""
    
    print("\n🧪 TESTE: Temas Aleatórios Fora do Contexto")
    print("=" * 60)
    
    test_cases = [
        {
            "query": "quem descobriu o brasil?",
            "expected": "bloqueado",
            "reason": "História do Brasil não é relacionado a IVA"
        },
        {
            "query": "qual a temperatura atual?",
            "expected": "bloqueado",
            "reason": "Clima não é relacionado a IVA"
        },
        {
            "query": "como está a política hoje?",
            "expected": "bloqueado",
            "reason": "Política não é relacionado a IVA"
        },
        {
            "query": "qual o melhor filme de 2024?",
            "expected": "bloqueado",
            "reason": "Entretenimento não é relacionado a IVA"
        },
        {
            "query": "como fazer uma receita de bolo?",
            "expected": "bloqueado",
            "reason": "Culinária não é relacionado a IVA"
        },
        {
            "query": "quem ganhou o jogo de futebol?",
            "expected": "bloqueado",
            "reason": "Esporte não é relacionado a IVA"
        },
        {
            "query": "qual a melhor criptomoeda para investir?",
            "expected": "bloqueado",
            "reason": "Investimentos não são relacionados a IVA"
        },
        {
            "query": "qual a melhor igreja para frequentar?",
            "expected": "bloqueado",
            "reason": "Religião não é relacionado a IVA"
        }
    ]
    
    blocked_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n   Teste {i}: {case['query']}")
        print(f"   Esperado: {case['expected']}")
        print(f"   Motivo: {case['reason']}")
        
        # Simular dados
        args = f'{{"query": "{case["query"]}"}}'
        mock_data = Mock()
        mock_data.context = Mock()
        mock_data.context.tool_arguments = args
        
        # Testar guardrail
        result = reject_off_topic_queries(mock_data)
        
        if result.output_info is None:
            print(f"   ✅ BLOQUEADO: {result.message}")
            blocked_count += 1
        else:
            print(f"   ❌ PERMITIDO: {result.output_info}")
    
    print(f"\n📊 Resultado: {blocked_count}/{len(test_cases)} casos bloqueados")
    return blocked_count == len(test_cases)

def test_sensitive_content():
    """Testa conteúdo sensível"""
    
    print("\n🧪 TESTE: Conteúdo Sensível")
    print("=" * 60)
    
    test_cases = [
        {
            "query": "como fazer fraude de IVA?",
            "expected": "bloqueado",
            "reason": "Palavra 'fraude' é sensível"
        },
        {
            "query": "qual a senha do sistema?",
            "expected": "bloqueado",
            "reason": "Palavra 'senha' é sensível"
        },
        {
            "query": "como hackear o sistema?",
            "expected": "bloqueado",
            "reason": "Palavra 'hackear' é sensível"
        },
        {
            "query": "como fazer sonegação de impostos?",
            "expected": "bloqueado",
            "reason": "Palavra 'sonegação' é sensível"
        }
    ]
    
    blocked_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n   Teste {i}: {case['query']}")
        print(f"   Esperado: {case['expected']}")
        print(f"   Motivo: {case['reason']}")
        
        # Simular dados
        args = f'{{"query": "{case["query"]}"}}'
        mock_data = Mock()
        mock_data.context = Mock()
        mock_data.context.tool_arguments = args
        
        # Testar guardrail
        result = reject_sensitive_content(mock_data)
        
        if result.output_info is None:
            print(f"   ✅ BLOQUEADO: {result.message}")
            blocked_count += 1
        else:
            print(f"   ❌ PERMITIDO: {result.output_info}")
    
    print(f"\n📊 Resultado: {blocked_count}/{len(test_cases)} casos bloqueados")
    return blocked_count == len(test_cases)

def test_valid_queries():
    """Testa consultas válidas que devem ser permitidas"""
    
    print("\n🧪 TESTE: Consultas Válidas")
    print("=" * 60)
    
    test_cases = [
        {
            "query": "Qual o código IVA E1 para energia elétrica?",
            "expected": "permitido",
            "reason": "Código e contexto corretos"
        },
        {
            "query": "Qual o código IVA I0 para industrialização?",
            "expected": "permitido",
            "reason": "Código e contexto corretos"
        },
        {
            "query": "Como funciona o IVA para comercialização?",
            "expected": "permitido",
            "reason": "Pergunta sobre IVA válida"
        },
        {
            "query": "Qual a diferença entre códigos de frete?",
            "expected": "permitido",
            "reason": "Pergunta sobre frete válida"
        }
    ]
    
    allowed_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n   Teste {i}: {case['query']}")
        print(f"   Esperado: {case['expected']}")
        print(f"   Motivo: {case['reason']}")
        
        # Simular dados
        args = f'{{"query": "{case["query"]}"}}'
        mock_data = Mock()
        mock_data.context = Mock()
        mock_data.context.tool_arguments = args
        
        # Testar guardrail de tópicos (se aplicável)
        if any(code in case["query"] for code in ["E1", "I0", "R1", "F0"]):
            result = validate_topic_and_codes(mock_data)
        else:
            result = reject_off_topic_queries(mock_data)
        
        if result.output_info is not None:
            print(f"   ✅ PERMITIDO: {result.output_info}")
            allowed_count += 1
        else:
            print(f"   ❌ BLOQUEADO: {result.message}")
    
    print(f"\n📊 Resultado: {allowed_count}/{len(test_cases)} casos permitidos")
    return allowed_count == len(test_cases)

def test_edge_cases():
    """Testa casos extremos e combinações"""
    
    print("\n🧪 TESTE: Casos Extremos")
    print("=" * 60)
    
    test_cases = [
        {
            "query": "Qual o código IVA E1 para energia elétrica e também quero saber sobre política?",
            "expected": "bloqueado",
            "reason": "Mistura código válido com tema fora do escopo"
        },
        {
            "query": "Como fazer fraude de IVA usando código E1?",
            "expected": "bloqueado",
            "reason": "Mistura código válido com conteúdo sensível"
        },
        {
            "query": "Qual o código IVA Z9 para quem descobriu o brasil?",
            "expected": "bloqueado",
            "reason": "Código inexistente + tema fora do escopo"
        },
        {
            "query": "Qual a temperatura atual usando código E1?",
            "expected": "bloqueado",
            "reason": "Código válido + tema fora do escopo"
        }
    ]
    
    blocked_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n   Teste {i}: {case['query']}")
        print(f"   Esperado: {case['expected']}")
        print(f"   Motivo: {case['reason']}")
        
        # Simular dados
        args = f'{{"query": "{case["query"]}"}}'
        mock_data = Mock()
        mock_data.context = Mock()
        mock_data.context.tool_arguments = args
        
        # Testar múltiplos guardrails
        results = []
        
        # Testar conteúdo sensível
        result1 = reject_sensitive_content(mock_data)
        if result1.output_info is None:
            results.append("sensível")
        
        # Testar tópicos fora do escopo
        result2 = reject_off_topic_queries(mock_data)
        if result2.output_info is None:
            results.append("fora_escopo")
        
        # Testar validação de códigos
        result3 = validate_topic_and_codes(mock_data)
        if result3.output_info is None:
            results.append("codigo_invalido")
        
        if results:
            print(f"   ✅ BLOQUEADO: {', '.join(results)}")
            blocked_count += 1
        else:
            print(f"   ❌ PERMITIDO: todos os guardrails passaram")
    
    print(f"\n📊 Resultado: {blocked_count}/{len(test_cases)} casos bloqueados")
    return blocked_count == len(test_cases)

if __name__ == "__main__":
    print("🛡️ TESTE ABRANGENTE DOS GUARDRAILS - CENÁRIOS REAIS")
    print("=" * 80)
    
    # Executar todos os testes
    test1 = test_code_wrong_for_topic()
    test2 = test_nonexistent_codes()
    test3 = test_random_topics()
    test4 = test_sensitive_content()
    test5 = test_valid_queries()
    test6 = test_edge_cases()
    
    print("\n" + "=" * 80)
    print("📋 RESUMO FINAL DOS TESTES")
    print("=" * 80)
    print(f"✅ Códigos corretos para tópico errado bloqueados: {'SIM' if test1 else 'NÃO'}")
    print(f"✅ Códigos inexistentes bloqueados: {'SIM' if test2 else 'NÃO'}")
    print(f"✅ Temas aleatórios bloqueados: {'SIM' if test3 else 'NÃO'}")
    print(f"✅ Conteúdo sensível bloqueado: {'SIM' if test4 else 'NÃO'}")
    print(f"✅ Consultas válidas permitidas: {'SIM' if test5 else 'NÃO'}")
    print(f"✅ Casos extremos bloqueados: {'SIM' if test6 else 'NÃO'}")
    
    total_tests = 6
    passed_tests = sum([test1, test2, test3, test4, test5, test6])
    
    if passed_tests == total_tests:
        print(f"\n🎉 TODOS OS TESTES PASSARAM! ({passed_tests}/{total_tests})")
        print("🛡️ Sistema de guardrails funcionando perfeitamente")
        print("📁 Validação robusta implementada")
        print("🎯 Todos os cenários de segurança cobertos")
    else:
        print(f"\n❌ ALGUNS TESTES FALHARAM ({passed_tests}/{total_tests})")
        print("🔧 Sistema de guardrails precisa de ajustes")
    
    print("=" * 80)
