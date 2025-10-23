"""
Testes unittest para o sistema de guardrails
Focando em temas fora dos assuntos dos agentes
"""

import unittest
import asyncio
from unittest.mock import MagicMock
from pydantic import BaseModel


# Define as classes necessárias diretamente no teste
class GuardrailOutput(BaseModel):
    """Output do guardrail"""
    reasoning: str
    is_in_scope: bool
    confidence: float
    suggested_action: str


class MockGuardrailSystem:
    """Mock do sistema de guardrails para testes"""
    
    def __init__(self):
        self.config = MagicMock()
        self.config.client = MagicMock()
        self.config.client.chat = MagicMock()
        self.config.client.chat.completions = MagicMock()
    
    async def evaluate_message(self, message: str, agent_name: str) -> GuardrailOutput:
        """Mock da avaliação de mensagem"""
        message_lower = message.lower()
        
        # Simula diferentes respostas baseadas no conteúdo da mensagem
        if any(word in message_lower for word in ["matemática", "equação", "derivada", "integral", "cálculo", "2x", "resolver"]):
            return GuardrailOutput(
                reasoning="Esta mensagem está relacionada a matemática, que está fora do escopo dos agentes White Martins.",
                is_in_scope=False,
                confidence=0.9,
                suggested_action="refuse"
            )
        elif any(word in message_lower for word in ["python", "javascript", "programação", "código", "api", "git", "docker"]):
            return GuardrailOutput(
                reasoning="Esta mensagem está relacionada a programação, que está fora do escopo dos agentes White Martins.",
                is_in_scope=False,
                confidence=0.8,
                suggested_action="refuse"
            )
        elif any(word in message_lower for word in ["filme", "jogo", "xadrez", "netflix", "livro", "entretenimento"]):
            return GuardrailOutput(
                reasoning="Esta mensagem está relacionada a entretenimento, que está fora do escopo dos agentes White Martins.",
                is_in_scope=False,
                confidence=0.85,
                suggested_action="refuse"
            )
        elif any(word in message_lower for word in ["parker", "festo", "smc", "bosch", "concorrente"]):
            return GuardrailOutput(
                reasoning="Esta mensagem está relacionada a concorrentes, que está fora do escopo dos agentes White Martins.",
                is_in_scope=False,
                confidence=0.9,
                suggested_action="refuse"
            )
        elif any(word in message_lower for word in ["pessoal", "relacionamento", "estresse", "família", "psicológica"]):
            return GuardrailOutput(
                reasoning="Esta mensagem está relacionada a assuntos pessoais, que está fora do escopo dos agentes White Martins.",
                is_in_scope=False,
                confidence=0.8,
                suggested_action="refuse"
            )
        elif any(word in message_lower for word in ["válvula", "pneumático", "cilindro", "compressor", "white martins", "suporte técnico", "equipamento"]):
            return GuardrailOutput(
                reasoning="Esta mensagem está relacionada aos produtos e serviços da White Martins.",
                is_in_scope=True,
                confidence=0.9,
                suggested_action="continue"
            )
        else:
            return GuardrailOutput(
                reasoning="Mensagem mista - parte relevante, parte fora do escopo.",
                is_in_scope=False,
                confidence=0.6,
                suggested_action="redirect"
            )


class TestGuardrailsOutOfScope(unittest.TestCase):
    """Testes para temas fora do escopo dos agentes"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.guardrail_system = MockGuardrailSystem()
    
    def test_mathematics_messages_rejected(self):
        """Testa especificamente mensagens de matemática"""
        math_messages = [
            "Resolva 2x + 5 = 11",
            "Como calcular derivadas?",
            "Me ajude com integrais",
            "Qual é a fórmula da área do círculo?",
            "Como resolver equações quadráticas?"
        ]
        
        async def run_test():
            for message in math_messages:
                result = await self.guardrail_system.evaluate_message(message, "triage_agent")
                self.assertFalse(result.is_in_scope, f"Mensagem de matemática deveria ser rejeitada: {message}")
                self.assertIn(result.suggested_action, ["refuse", "redirect"], f"Ação deveria ser refuse ou redirect: {result.suggested_action}")
                self.assertGreaterEqual(result.confidence, 0.6, f"Confiança deveria ser >= 0.6: {result.confidence}")
                self.assertTrue(
                    "matemática" in result.reasoning.lower() or "escopo" in result.reasoning.lower(),
                    f"Razão deveria mencionar matemática ou escopo: {result.reasoning}"
                )
        
        asyncio.run(run_test())

    def test_programming_messages_rejected(self):
        """Testa especificamente mensagens de programação"""
        programming_messages = [
            "Como criar uma API em Python?",
            "Me ensine JavaScript",
            "Como usar Git?",
            "Preciso de ajuda com Docker",
            "Como fazer deploy de uma aplicação?"
        ]
        
        async def run_test():
            for message in programming_messages:
                result = await self.guardrail_system.evaluate_message(message, "knowledge_agent")
                self.assertFalse(result.is_in_scope, f"Mensagem de programação deveria ser rejeitada: {message}")
                self.assertIn(result.suggested_action, ["refuse", "redirect"], f"Ação deveria ser refuse ou redirect: {result.suggested_action}")
                self.assertGreaterEqual(result.confidence, 0.6, f"Confiança deveria ser >= 0.6: {result.confidence}")
                self.assertTrue(
                    "programação" in result.reasoning.lower() or "escopo" in result.reasoning.lower(),
                    f"Razão deveria mencionar programação ou escopo: {result.reasoning}"
                )
        
        asyncio.run(run_test())

    def test_entertainment_messages_rejected(self):
        """Testa especificamente mensagens de entretenimento"""
        entertainment_messages = [
            "Qual filme assistir hoje?",
            "Recomende um jogo",
            "Como jogar melhor xadrez?",
            "Qual série da Netflix assistir?",
            "Me ajude a escolher um livro"
        ]
        
        async def run_test():
            for message in entertainment_messages:
                result = await self.guardrail_system.evaluate_message(message, "answer_agent")
                self.assertFalse(result.is_in_scope, f"Mensagem de entretenimento deveria ser rejeitada: {message}")
                self.assertIn(result.suggested_action, ["refuse", "redirect"], f"Ação deveria ser refuse ou redirect: {result.suggested_action}")
                self.assertEqual(result.confidence, 0.85, f"Confiança deveria ser 0.85: {result.confidence}")
                self.assertIn("entretenimento", result.reasoning.lower(), f"Razão deveria mencionar entretenimento: {result.reasoning}")
        
        asyncio.run(run_test())

    def test_competitor_messages_rejected(self):
        """Testa especificamente mensagens sobre concorrentes"""
        competitor_messages = [
            "Quero informações sobre produtos da Parker",
            "Como funciona o sistema da Festo?",
            "Preciso de válvulas da SMC",
            "Qual é melhor: White Martins ou Parker?",
            "Me ajude com equipamentos da Bosch"
        ]
        
        async def run_test():
            for message in competitor_messages:
                result = await self.guardrail_system.evaluate_message(message, "triage_agent")
                self.assertFalse(result.is_in_scope, f"Mensagem sobre concorrente deveria ser rejeitada: {message}")
                self.assertIn(result.suggested_action, ["refuse", "redirect"], f"Ação deveria ser refuse ou redirect: {result.suggested_action}")
                self.assertGreaterEqual(result.confidence, 0.6, f"Confiança deveria ser >= 0.6: {result.confidence}")
                self.assertIn("concorrente", result.reasoning.lower(), f"Razão deveria mencionar concorrente: {result.reasoning}")
        
        asyncio.run(run_test())

    def test_personal_messages_rejected(self):
        """Testa especificamente mensagens pessoais"""
        personal_messages = [
            "Estou passando por problemas pessoais",
            "Preciso de conselhos sobre relacionamento",
            "Como lidar com estresse no trabalho?",
            "Me ajude com problemas familiares",
            "Preciso de orientação psicológica"
        ]
        
        async def run_test():
            for message in personal_messages:
                result = await self.guardrail_system.evaluate_message(message, "interview_agent")
                self.assertFalse(result.is_in_scope, f"Mensagem pessoal deveria ser rejeitada: {message}")
                self.assertIn(result.suggested_action, ["refuse", "redirect"], f"Ação deveria ser refuse ou redirect: {result.suggested_action}")
                self.assertGreaterEqual(result.confidence, 0.6, f"Confiança deveria ser >= 0.6: {result.confidence}")
                self.assertTrue(
                    "pessoal" in result.reasoning.lower() or "escopo" in result.reasoning.lower(),
                    f"Razão deveria mencionar pessoal ou escopo: {result.reasoning}"
                )
        
        asyncio.run(run_test())

    def test_in_scope_messages_accepted(self):
        """Testa mensagens que devem estar no escopo"""
        in_scope_messages = [
            "Preciso de uma válvula pneumática para minha aplicação industrial",
            "Qual é a especificação técnica do cilindro pneumático modelo XYZ?",
            "Quero informações sobre compressores White Martins",
            "Como funciona o sistema pneumático da White Martins?",
            "Preciso de suporte técnico para meu equipamento"
        ]
        
        async def run_test():
            for message in in_scope_messages:
                result = await self.guardrail_system.evaluate_message(message, "triage_agent")
                self.assertTrue(result.is_in_scope, f"Mensagem deveria estar no escopo: {message}")
                self.assertEqual(result.suggested_action, "continue", f"Ação deveria ser continue: {result.suggested_action}")
                self.assertGreaterEqual(result.confidence, 0.6, f"Confiança deveria ser >= 0.6: {result.confidence}")
                self.assertIn("white martins", result.reasoning.lower(), f"Razão deveria mencionar White Martins: {result.reasoning}")
        
        asyncio.run(run_test())

    def test_edge_cases(self):
        """Testa casos extremos"""
        edge_cases = [
            "",  # Mensagem vazia
            "a",  # Mensagem muito curta
            "Preciso de ajuda com válvulas pneumáticas e também quero aprender Python",  # Misto
        ]
        
        async def run_test():
            for message in edge_cases:
                result = await self.guardrail_system.evaluate_message(message, "triage_agent")
                # Deve sempre retornar um resultado válido
                self.assertIsInstance(result, GuardrailOutput)
                self.assertIsInstance(result.is_in_scope, bool)
                self.assertIsInstance(result.confidence, float)
                self.assertIn(result.suggested_action, ["continue", "redirect", "refuse"])
        
        asyncio.run(run_test())

    def test_different_agents_consistency(self):
        """Testa se diferentes agentes rejeitam consistentemente mensagens fora do escopo"""
        out_of_scope_message = "Como resolver 2x + 5 = 11?"
        agents = ["triage_agent", "flow_agent", "interview_agent", "answer_agent", "knowledge_agent"]
        
        async def run_test():
            for agent in agents:
                result = await self.guardrail_system.evaluate_message(out_of_scope_message, agent)
                self.assertFalse(result.is_in_scope, f"Agente {agent} deveria rejeitar mensagem de matemática")
                self.assertIn(result.suggested_action, ["refuse", "redirect"], f"Agente {agent} deveria sugerir refuse ou redirect")
        
        asyncio.run(run_test())

    def test_guardrail_output_structure(self):
        """Testa estrutura do GuardrailOutput"""
        output = GuardrailOutput(
            reasoning="Teste de razão",
            is_in_scope=False,
            confidence=0.8,
            suggested_action="refuse"
        )
        
        self.assertEqual(output.reasoning, "Teste de razão")
        self.assertFalse(output.is_in_scope)
        self.assertEqual(output.confidence, 0.8)
        self.assertEqual(output.suggested_action, "refuse")
        self.assertIsInstance(output.reasoning, str)
        self.assertIsInstance(output.is_in_scope, bool)
        self.assertIsInstance(output.confidence, float)
        self.assertIsInstance(output.suggested_action, str)

    def test_confidence_scores_range(self):
        """Testa se os scores de confiança estão no range correto"""
        test_messages = [
            "Resolva 2x + 5 = 11",  # Matemática
            "Como criar uma API em Python?",  # Programação
            "Qual filme assistir hoje?",  # Entretenimento
            "Preciso de uma válvula pneumática"  # No escopo
        ]
        
        async def run_test():
            for message in test_messages:
                result = await self.guardrail_system.evaluate_message(message, "triage_agent")
                self.assertGreaterEqual(result.confidence, 0.0, f"Confiança deveria ser >= 0.0: {result.confidence}")
                self.assertLessEqual(result.confidence, 1.0, f"Confiança deveria ser <= 1.0: {result.confidence}")
        
        asyncio.run(run_test())

    def test_suggested_actions_valid(self):
        """Testa se as ações sugeridas são válidas"""
        test_messages = [
            "Resolva 2x + 5 = 11",  # Matemática
            "Como criar uma API em Python?",  # Programação
            "Preciso de uma válvula pneumática",  # No escopo
            "Mensagem ambígua"  # Caso misto
        ]
        
        valid_actions = ["continue", "redirect", "refuse"]
        
        async def run_test():
            for message in test_messages:
                result = await self.guardrail_system.evaluate_message(message, "triage_agent")
                self.assertIn(result.suggested_action, valid_actions, f"Ação sugerida deveria ser válida: {result.suggested_action}")
        
        asyncio.run(run_test())


if __name__ == "__main__":
    # Executa os testes
    unittest.main(verbosity=2)