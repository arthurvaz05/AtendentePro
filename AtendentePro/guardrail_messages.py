"""
Sistema de Mensagens de Guardrails
===================================

Carrega mensagens customizadas para diferentes clientes quando guardrails são ativados.
"""

import os
import yaml
from typing import Dict, Any, Optional


class GuardrailMessages:
    """Carregador de mensagens de guardrails customizadas por cliente"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
    
    def _find_config_file(self) -> str:
        """Encontra o arquivo de mensagens apropriado"""
        # Ordem de prioridade: específico do cliente -> standard -> fallback
        config_paths = [
            "AtendentePro/Template/White_Martins/guardrail_messages.yaml",
            "AtendentePro/Template/standard/guardrail_messages.yaml",
            "guardrail_messages.yaml"
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                return path
        
        # Se nenhum arquivo for encontrado, retorna o primeiro como fallback
        return config_paths[0]
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão caso não encontre arquivo"""
        return {
            "guardrail_messages": {
                "out_of_scope": {
                    "title": "🚫 Pergunta fora do escopo",
                    "message": "Desculpe, só posso ajudar com questões relacionadas aos nossos serviços.",
                    "short_message": "Pergunta fora do escopo."
                },
                "error_fallback": {
                    "title": "⚠️ Erro no sistema",
                    "message": "Erro técnico. Tente novamente.",
                    "short_message": "Erro técnico."
                }
            },
            "settings": {
                "show_detailed_message": True,
                "include_suggestions": True,
                "add_to_conversation": True
            }
        }
    
    def get_out_of_scope_message(self, detailed: bool = None) -> str:
        """Retorna mensagem para perguntas fora do escopo"""
        if detailed is None:
            detailed = self.config.get("settings", {}).get("show_detailed_message", True)
        
        messages = self.config.get("guardrail_messages", {}).get("out_of_scope", {})
        
        if detailed:
            return messages.get("message", "Desculpe, só posso ajudar com questões relacionadas aos nossos serviços.")
        else:
            return messages.get("short_message", "Pergunta fora do escopo.")
    
    def get_error_fallback_message(self, detailed: bool = None) -> str:
        """Retorna mensagem para erros de sistema"""
        if detailed is None:
            detailed = self.config.get("settings", {}).get("show_detailed_message", True)
        
        messages = self.config.get("guardrail_messages", {}).get("error_fallback", {})
        
        if detailed:
            return messages.get("message", "Erro técnico. Tente novamente.")
        else:
            return messages.get("short_message", "Erro técnico.")
    
    def get_title(self, message_type: str) -> str:
        """Retorna título da mensagem"""
        messages = self.config.get("guardrail_messages", {}).get(message_type, {})
        return messages.get("title", "🚫 Aviso")


# Instância global para uso fácil
guardrail_messages = GuardrailMessages()


def get_guardrail_message(message_type: str = "out_of_scope", detailed: bool = None) -> str:
    """
    Função de conveniência para obter mensagens de guardrails
    
    Args:
        message_type: Tipo da mensagem ("out_of_scope" ou "error_fallback")
        detailed: Se deve retornar mensagem detalhada (None = usar configuração)
        
    Returns:
        Mensagem formatada
    """
    if message_type == "out_of_scope":
        return guardrail_messages.get_out_of_scope_message(detailed)
    elif message_type == "error_fallback":
        return guardrail_messages.get_error_fallback_message(detailed)
    else:
        return "Mensagem não encontrada."
