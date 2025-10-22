#!/usr/bin/env python3
"""
Debug do Regex para Códigos IVA
"""

import re

def debug_regex():
    """Debug do regex para códigos IVA"""
    
    test_queries = [
        "Qual o código IVA E1 para industrialização?",
        "Qual o código IVA I0 para frete?",
        "Qual o código IVA Z9 para energia elétrica?",
        "Qual o código IVA XX para industrialização?",
        "Qual o código IVA ABC para comercialização?"
    ]
    
    print("🔍 DEBUG DO REGEX PARA CÓDIGOS IVA")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        # Testar diferentes padrões
        patterns = [
            r'\b([A-Z]\d|[A-Z]{2,3}|\d{2,3})\b',
            r'\b([A-Z]\d|[A-Z]{2}|\d{2})\b',
            r'\b([A-Z]\d|[A-Z]{2})\b',
            r'\b([A-Z]\d)\b',
            r'\b([A-Z]{2})\b'
        ]
        
        for i, pattern in enumerate(patterns, 1):
            matches = re.findall(pattern, query)
            print(f"  Padrão {i}: {pattern}")
            print(f"    Matches: {matches}")
        
        # Testar com filtro de palavras comuns
        common_words = {"QUAL", "PARA", "COM", "SEM", "DOS", "DAS", "DO", "DA", "DE", "EM", "NA", "NO", "IVA", "CODIGO"}
        pattern = r'\b([A-Z]\d|[A-Z]{2,3}|\d{2,3})\b'
        matches = re.findall(pattern, query)
        filtered_matches = [match.upper() for match in matches if match.upper() not in common_words]
        print(f"  Com filtro: {filtered_matches}")

if __name__ == "__main__":
    debug_regex()
