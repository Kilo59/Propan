from propan import PropanApp, KafkaBroker

broker = KafkaBroker()

@broker.handler("ping")
async def healthcheck(msg: str) -> str:
    return "pong" if msg == "ping" else "wrong"

app = PropanApp(broker)