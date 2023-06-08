from propan import PropanApp, RabbitBroker

broker = RabbitBroker()

@broker.handler("ping")
async def healthcheck(msg: str) -> str:
    return "pong" if msg == "ping" else "wrong"

app = PropanApp(broker)