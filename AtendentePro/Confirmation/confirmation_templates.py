from __future__ import annotations

from AtendentePro.Confirmation.confirmation_config import ConfirmationConfig

_config = ConfirmationConfig.load()

confirmation_about = _config.about
confirmation_format = _config.format
confirmation_template = _config.template
