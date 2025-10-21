from __future__ import annotations

from types import SimpleNamespace

from AtendentePro.Interview.interview_models import InterviewOutput
from AtendentePro.Template.White_Martins.answer_config import AnswerTopic
from AtendentePro.context import ContextNote
from AtendentePro.utils.handoff import append_handoff_summary


class DummyResult:
    def __init__(self, final_output: InterviewOutput):
        self.final_output = final_output
        self._input = [{"role": "user", "content": "Olá"}]
        self.new_items = []
        self.last_agent = SimpleNamespace(name="Interview Agent")

    def to_input_list(self):
        return list(self._input)


def test_append_handoff_summary_updates_context_and_items():
    output = InterviewOutput(topic=AnswerTopic.COMPRA_COMERCIALIZACAO, answers={"1": "a"})
    result = DummyResult(output)
    context = ContextNote()

    new_items = append_handoff_summary(
        result,
        context,
        payload_key="interview_output",
        next_agent_hint="Answer Agent",
        summary_label="interview",
    )

    stored_summary = context.handoff_summaries["interview"]
    assert stored_summary["payload"]["topic"] == AnswerTopic.COMPRA_COMERCIALIZACAO
    assert stored_summary["next_agent_hint"] == "Answer Agent"
    assert any(
        item.get("role") == "assistant" and "[HANDOFF_SUMMARY]" in item.get("content", "")
        for item in new_items
    )
