from __future__ import annotations

from AtendentePro.Knowledge.knowledge_config import KnowledgeConfig

_config = KnowledgeConfig.load()

knowledge_about = _config.about
knowledge_format = _config.format
knowledge_template = _config.template
