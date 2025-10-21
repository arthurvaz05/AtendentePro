from __future__ import annotations

from AtendentePro.Answer.answer_config import AnswerConfig
from AtendentePro.Template.White_Martins.answer_config import AnswerOutput, AnswerTopic

_config = AnswerConfig.load()

answer_template = _config.answer_template

__all__ = ["AnswerTopic", "AnswerOutput", "answer_template"]
