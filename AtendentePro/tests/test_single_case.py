#!/usr/bin/env python3
"""
Teste Rápido - Apenas Primeiro Caso
"""

import json
import re
from unittest.mock import Mock

# Configuração de teste simplificada
test_config = {
    "topics": {
        "compra_industrializacao": {
            "description": "Compra para industrialização — material manufaturado ou processo produtivo",
            "codes": ["I0", "ID", "IE", "I8", "I5", "I9", "I2", "I7", "I1", "I3", "I4"]
        },
        "aquisicao_energia_eletrica": {
            "description": "Aquisição de energia elétrica — produtiva vs administrativa",
            "codes": ["E1", "E2", "E3", "E4", "E0"]
        }
    }
}

def validate_topic_and_codes(data):
    """Valida tópicos e códigos específicos por tópico"""
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return Mock(output_info="Argumentos JSON inválidos")

    topics = test_config.get("topics", {})
    
    if not topics:
        return Mock(output_info="Validação de tópicos não configurada")

    for key, value in args.items():
        value_str = str(value)  # Manter maiúsculas para o regex
        print(f"DEBUG: Analisando '{value_str}'")
        
        # Procurar por códigos IVA no texto
        code_pattern = r'\b([A-Z]\d|[A-Z]{2,3}|\d{2,3})\b'
        matches = re.findall(code_pattern, value_str)
        
        # Filtrar palavras comuns
        common_words = {"QUAL", "PARA", "COM", "SEM", "DOS", "DAS", "DO", "DA", "DE", "EM", "NA", "NO", "IVA", "CODIGO"}
        matches = [match.upper() for match in matches if match.upper() not in common_words]
        
        print(f"DEBUG: Códigos encontrados: {matches}")
        
        # Converter para minúsculas apenas para verificação de contexto
        value_str_lower = value_str.lower()
        
        if matches:
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
                
                # Verificar contexto
                topic_keywords = {
                    "compra_industrializacao": ["industrialização", "industrial", "produção", "manufaturado"],
                    "aquisicao_energia_eletrica": ["energia", "elétrica", "eletricidade"]
                }
                
                context_matches = False
                if topic_for_code in topic_keywords:
                    for keyword in topic_keywords[topic_for_code]:
                        if keyword in value_str_lower:
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

def test_single_case():
    """Testa apenas um caso"""
    
    print("🧪 TESTE: Caso Individual")
    print("=" * 60)
    print("Query: 'Qual o código IVA E1 para industrialização?'")
    print("Esperado: BLOQUEADO (E1 é para energia, não industrialização)")
    print("=" * 60)
    
    # Simular dados
    args = '{"query": "Qual o código IVA E1 para industrialização?"}'
    mock_data = Mock()
    mock_data.context = Mock()
    mock_data.context.tool_arguments = args
    
    # Testar guardrail
    result = validate_topic_and_codes(mock_data)
    
    print("\n" + "=" * 60)
    print("RESULTADO FINAL:")
    print(f"Bloqueado: {result.output_info is None}")
    print(f"Mensagem: {result.message if hasattr(result, 'message') else 'N/A'}")
    print("=" * 60)

if __name__ == "__main__":
    test_single_case()
