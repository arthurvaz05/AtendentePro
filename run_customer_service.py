#!/usr/bin/env python3
"""
Script para executar o Customer Service Example
"""

# Importar configurações PRIMEIRO
import config

# Agora importar e executar o customer service
import asyncio
import sys
import os

# Adicionar o caminho dos exemplos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'openai-agents-python', 'examples'))

# Importar o módulo customer_service
from customer_service.main import main

if __name__ == "__main__":
    print("🚀 Customer Service Example iniciado!")
    print("Digite suas mensagens (Ctrl+C para sair)")
    print("-" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Customer Service finalizado!")
