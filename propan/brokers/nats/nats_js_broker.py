# TODO: remove mypy ignore at complete
# type: ignore
from functools import wraps
from typing import Any, Optional

import nats
from nats.aio.msg import Msg
from nats.js.client import JetStreamContext

from propan.brokers.nats.nats_broker import NatsBroker
from propan.brokers.nats.schemas import JetStream
from propan.brokers.push_back_watcher import BaseWatcher, WatcherContext
from propan.types import AnyDict, DecoratedCallable


class NatsJSBroker(NatsBroker):
    _js: Optional[JetStream] = None
    _connection: Optional[JetStreamContext] = None

    def __init__(self, *args: Any, jetstream: JetStream, **kwargs: AnyDict):
        super().__init__(*args, **kwargs)
        self._js = jetstream

    async def _connect(self, *args: Any, **kwargs: AnyDict) -> JetStreamContext:
        assert self._js

        nc = await nats.connect(*args, **kwargs)

        return await nc.jetstream(
            **self._js.dict(include={"prefix", "domain", "timeout"})
        )

    @staticmethod
    def _process_message(
        func: DecoratedCallable, watcher: Optional[BaseWatcher] = None
    ) -> DecoratedCallable:
        @wraps(func)
        async def wrapper(message: Msg) -> Any:
            if watcher is None:
                return await func(message)
            async with WatcherContext(
                watcher,
                message.message_id,
                on_success=message.ack,
                on_error=message.nak,
                on_max=message.term,
            ):
                await message.in_progress()
                return await func(message)

        return wrapper
