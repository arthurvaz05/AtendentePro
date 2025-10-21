"""Testes para os modelos de dados."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project and package roots are on sys.path for absolute imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

PACKAGE_ROOT = PROJECT_ROOT / "AtendentePro"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.append(str(PACKAGE_ROOT))

from AtendentePro.Template.White_Martins.answer_config import AnswerOutput, AnswerTopic  # noqa: E402
from AtendentePro.Interview.interview_models import InterviewOutput  # noqa: E402
from AtendentePro.Flow.flow_models import FlowOutput  # noqa: E402


def test_answer_topic_enum():
    """Testa o enum AnswerTopic."""
    # Verifica se todos os tópicos esperados existem
    expected_topics = [
        "compra_industrializacao",
        "compra_comercializacao", 
        "compra_ativo_operacional",
        "compra_ativo_projeto",
        "consumo_administrativo_ativo_nao_operacional",
        "aquisicao_frete",
        "aquisicao_energia_eletrica",
        "aquisicao_servicos_ligados_a_operacao",
        "aquisicao_servicos_nao_ligados_a_operacao"
    ]
    
    for topic in expected_topics:
        assert hasattr(AnswerTopic, topic.upper()), f"Missing topic: {topic}"
        assert getattr(AnswerTopic, topic.upper()).value == topic


def test_answer_output_model():
    """Testa o modelo AnswerOutput."""
    # Testa criação com dados válidos
    output = AnswerOutput(
        topic=AnswerTopic.COMPRA_INDUSTRIALIZACAO,
        code="I0"
    )
    
    assert output.topic == AnswerTopic.COMPRA_INDUSTRIALIZACAO
    assert output.code == "I0"
    
    # Testa validação de tipo
    assert isinstance(output.topic, AnswerTopic)
    assert isinstance(output.code, str)


def test_interview_output_model():
    """Testa o modelo InterviewOutput."""
    # Testa criação com dados válidos
    output = InterviewOutput(
        topic=AnswerTopic.COMPRA_COMERCIALIZACAO,
        answers={"1.1": "SIM", "1.2": "NÃO"}
    )
    
    assert output.topic == AnswerTopic.COMPRA_COMERCIALIZACAO
    assert output.answers == {"1.1": "SIM", "1.2": "NÃO"}
    assert isinstance(output.answers, dict)


def test_flow_output_model():
    """Testa o modelo FlowOutput."""
    # Testa criação com dados válidos
    output = FlowOutput(
        selected_topic=AnswerTopic.COMPRA_ATIVO_OPERACIONAL,
        user_answer="Quero comprar uma máquina",
        reasoning="Usuário mencionou compra de máquina"
    )
    
    assert output.selected_topic == AnswerTopic.COMPRA_ATIVO_OPERACIONAL
    assert output.user_answer == "Quero comprar uma máquina"
    assert output.reasoning == "Usuário mencionou compra de máquina"


def test_models_serialization():
    """Testa serialização dos modelos."""
    # AnswerOutput
    answer = AnswerOutput(topic=AnswerTopic.AQUISICAO_FRETE, code="F0")
    answer_dict = answer.model_dump()
    assert answer_dict["topic"] == "aquisicao_frete"
    assert answer_dict["code"] == "F0"
    
    # InterviewOutput
    interview = InterviewOutput(
        topic=AnswerTopic.COMPRA_INDUSTRIALIZACAO,
        answers={"1.1": "NÃO"}
    )
    interview_dict = interview.model_dump()
    assert interview_dict["topic"] == "compra_industrializacao"
    assert interview_dict["answers"] == {"1.1": "NÃO"}
    
    # FlowOutput
    flow = FlowOutput(
        selected_topic=AnswerTopic.COMPRA_COMERCIALIZACAO,
        user_answer="Teste",
        reasoning="Teste reasoning"
    )
    flow_dict = flow.model_dump()
    assert flow_dict["selected_topic"] == "compra_comercializacao"
    assert flow_dict["user_answer"] == "Teste"
    assert flow_dict["reasoning"] == "Teste reasoning"


def test_models_validation():
    """Testa validação dos modelos."""
    # Testa AnswerOutput com tópico inválido
    try:
        AnswerOutput(topic="invalid_topic", code="I0")
        assert False, "Should have raised validation error"
    except Exception:
        pass  # Esperado
    
    # Testa InterviewOutput com respostas vazias
    interview = InterviewOutput(
        topic=AnswerTopic.COMPRA_INDUSTRIALIZACAO,
        answers={}
    )
    assert interview.answers == {}


def test_answer_output_allowed_codes():
    """Testa o sistema de códigos permitidos."""
    # Verifica se o atributo existe
    assert hasattr(AnswerOutput, 'ALLOWED_CODES_BY_TOPIC')
    assert isinstance(AnswerOutput.ALLOWED_CODES_BY_TOPIC, dict)
    
    # Verifica se o método set_allowed_codes existe
    assert hasattr(AnswerOutput, 'set_allowed_codes')
    assert callable(AnswerOutput.set_allowed_codes)
