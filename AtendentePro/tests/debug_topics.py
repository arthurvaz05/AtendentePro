#!/usr/bin/env python3
"""
Teste de Debug - Validação de Contexto por Tópico
"""

import json
import re
from unittest.mock import Mock

# Configuração de teste simplificada
test_config = {
    "topics": {
        "aquisicao_energia_eletrica": {
            "description": "Aquisição de energia elétrica — produtiva vs administrativa",
            "codes": ["E1", "E2", "E3", "E4", "E0"]
        }
    }
}

def debug_validate_topic_and_codes(data):
    """Debug da validação de tópicos e códigos"""
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return Mock(output_info="Argumentos JSON inválidos")

    topics = test_config.get("topics", {})
    
    print(f"DEBUG: Tópicos carregados: {list(topics.keys())}")
    
    for key, value in args.items():
        value_str = str(value).lower()
        print(f"DEBUG: Analisando '{value_str}'")
        
        # Procurar por códigos IVA no texto
        code_pattern = r'\b([A-Za-z]\d|[A-Za-z]{2})\b'  # Aceitar maiúsculas e minúsculas
        matches = re.findall(code_pattern, value_str)
        matches = [match.upper() for match in matches]  # Converter para maiúsculas
        print(f"DEBUG: Códigos encontrados: {matches}")
        
        if matches:
            # Para cada código encontrado, verificar se está no tópico correto
            for code in matches:
                print(f"DEBUG: Verificando código '{code}'")
                code_found_in_topic = False
                topic_for_code = None
                
                # Encontrar em qual tópico o código está
                for topic_name, topic_data in topics.items():
                    if code in topic_data.get("codes", []):
                        code_found_in_topic = True
                        topic_for_code = topic_name
                        print(f"DEBUG: Código '{code}' encontrado no tópico '{topic_name}'")
                        break
                
                if not code_found_in_topic:
                    print(f"DEBUG: Código '{code}' não encontrado em nenhum tópico")
                    return Mock(
                        output_info=None,
                        message=f"🚨 Código IVA '{code}' não encontrado em nenhum tópico válido"
                    )
                
                # Verificar se o contexto da pergunta corresponde ao tópico do código
                topic_keywords = {
                    "aquisicao_energia_eletrica": ["energia", "elétrica", "eletricidade"]
                }
                
                print(f"DEBUG: Tópico do código: '{topic_for_code}'")
                print(f"DEBUG: Palavras-chave do tópico: {topic_keywords.get(topic_for_code, [])}")
                
                # Verificar se o contexto da pergunta corresponde ao tópico
                context_matches = False
                if topic_for_code in topic_keywords:
                    for keyword in topic_keywords[topic_for_code]:
                        print(f"DEBUG: Verificando palavra-chave '{keyword}' em '{value_str}'")
                        if keyword in value_str:
                            context_matches = True
                            print(f"DEBUG: Palavra-chave '{keyword}' encontrada!")
                            break
                
                print(f"DEBUG: Contexto corresponde: {context_matches}")
                
                if not context_matches:
                    topic_description = topics[topic_for_code].get("description", "")
                    print(f"DEBUG: Bloqueando - contexto não corresponde")
                    return Mock(
                        output_info=None,
                        message=f"🚨 Código IVA '{code}' não corresponde ao contexto da pergunta. Este código é para: {topic_description}"
                    )

    print("DEBUG: Validação passou")
    return Mock(output_info="Tópicos e códigos validados")

def test_debug_context():
    """Teste de debug para contexto incompatível"""
    
    print("🔍 DEBUG: Teste de Contexto Incompatível")
    print("=" * 60)
    print("Pergunta: 'Qual o código IVA E1 para futebol?'")
    print("=" * 60)
    
    # Simular dados de entrada com código correto mas contexto errado
    context_mismatch_args = '{"query": "Qual o código IVA E1 para futebol?"}'
    
    # Criar mock data
    mock_data = Mock()
    mock_data.context = Mock()
    mock_data.context.tool_arguments = context_mismatch_args
    
    # Testar guardrail
    result = debug_validate_topic_and_codes(mock_data)
    
    print("\n" + "=" * 60)
    print("RESULTADO FINAL:")
    print(f"Bloqueado: {result.output_info is None}")
    print(f"Mensagem: {result.message if hasattr(result, 'message') else 'N/A'}")
    print("=" * 60)

if __name__ == "__main__":
    test_debug_context()
