from pathlib import Path
from typing import Sequence

from propan.cli.startproject.utils import write_file


def create_app_file(
    app_dir: Path,
    broker_annotation: str,
    imports: Sequence[str] = (),
    broker_init: Sequence[str] = ("    await broker.connect(settings.broker.url)",),
) -> None:
    write_file(
        app_dir / "serve.py",
        "import logging",
        "from typing import Optional",
        "",
        *imports,
        "from propan import PropanApp",
        f"from propan.annotations import {broker_annotation}, ContextRepo",
        "",
        "from core import broker",
        "from config import init_settings",
        "",
        "from apps import *  # import to register handlers  # NOQA",
        "",
        "",
        "app = PropanApp(broker)",
        "",
        "",
        "@app.on_startup",
        f"async def init_app(broker: {broker_annotation}, context: ContextRepo, env: Optional[str] = None):",
        "    settings = init_settings(env)",
        '    context.set_global("settings", settings)',
        "",
        "    logger_level = logging.DEBUG if settings.debug else logging.INFO",
        "    app.logger.setLevel(logger_level)",
        "    broker.logger.setLevel(logger_level)",
        "",
        *broker_init,
        "",
        "",
        'if __name__ == "__main__":',
        "    app.run()",
    )
