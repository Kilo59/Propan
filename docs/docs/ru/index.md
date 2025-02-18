<p align="center">
    <img src="assets/img/logo-no-background.png" alt="Propan logo" style="height: 250px; width: 600px;"/>
</p>

<p align="center">
    <a href="https://github.com/Lancetnik/Propan/actions/workflows/tests.yml" target="_blank">
        <img src="https://github.com/Lancetnik/Propan/actions/workflows/tests.yml/badge.svg" alt="Tests coverage"/>
    </a>
    <a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/lancetnik/propan" target="_blank">
        <img src="https://coverage-badge.samuelcolvin.workers.dev/lancetnik/propan.svg" alt="Coverage">
    </a>
    <a href="https://pypi.org/project/propan" target="_blank">
        <img src="https://img.shields.io/pypi/v/propan?label=pypi%20package" alt="Package version">
    </a>
    <a href="https://pepy.tech/project/propan" target="_blank">
        <img src="https://static.pepy.tech/personalized-badge/propan?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads" alt="downloads"/>
    </a>
    <br/>
    <a href="https://pypi.org/project/propan" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/propan.svg" alt="Supported Python versions">
    </a>
    <a href="https://github.com/Lancetnik/Propan/blob/main/LICENSE" target="_blank">
        <img alt="GitHub" src="https://img.shields.io/github/license/Lancetnik/Propan?color=%23007ec6">
    </a>
</p>

# Propan

**Propan** - это *<s>еще один HTTP</s>* **декларативный Python MQ фреймворк**. Он идет по стопам [*fastapi*]({{ urls.fastapi }}){target="_blank"}, максимально упрощая написание кода и предоставляя все удобства инструментов, которые до этого существовали только в мире HTTP фремворков, однако, создан для работы с различными брокерами сообщений на основе AMQP, MQTT и др. протоколов.

Он идеально подходит для создания реактивных микросервисов на основе архитектуры [Messaging](https://microservices.io/patterns/communication-style/messaging.html){target="_blank"}.

Это современный, высокоуровневый фреймворк, разработанный на основе популярных *python* библиотек для работы со специфичными брокерами, а в его основе лежит [*pydantic*]({{ urls.pydantic }}){target="_blank"}, идеи [*fastapi*]({{ urls.fastapi }}){target="_blank"} and [*pytest*]({{ urls.pytest }}){target="_blank"}.

---

### Ключевые особенности

* **Простота**: спроектирован для максимальной простоты изучения и использования.
* **Интуитивность**: Отличная поддержка IDE, автодополнение даже в *vim*`е.
* [**Управление зависимостями**](getting_started/1_quick-start/#_4): Эффективное переиспользование за счет аннотации типов. Доступ к зависимостями во всем стеке вызова.
* [**Интeграция**](getting_started/1_quick-start/#http): Propan полностью совместим с [любыми HTTP фреймворками](integrations/1_integrations-index/)
* **Независимость от брокеров**: Единый интерфейс для популярных брокеров:
    * **Redis** (основан на [redis-py]({{ urls.redis }}){target="_blank"})
    * **RabbitMQ** (основан на [aio-pika]({{ urls.aio_pika }}){target="_blank"})
    * **Kafka** (основан на [aiokafka]({{ urls.aiokafka }}){target="_blank"})
    * **SQS** (основан на [aiobotocore]({{ urls.aiobotocore }}){target="_blank"})
    * **Nats** (основан на [nats-py]({{ urls.nats_py }}){target="_blank"})
* [**RPC**](getting_started/4_broker/5_rpc/): Фреймворк поддерживает RPC запросы поверх брокеров сообщений, что позволит выполнять длительные операции на удаленных сервисах асинхронно.
* [**Скорость разработки**](getting_started/2_cli/): собственный *CLI* инструмент предоставляет отличный опыт разработки:
    * Полностью совместимый с любым фреймворком способ управлять окружением проекта
    * *hot reloading* при изменениях в коде
    * Готовые шаблоны проекта
* [**Тестируемость**](getting_started/7_testing): **Propan** позволяет тестировать ваше приложение без внешних зависимостей: вам не нужно поднимать брокер сообщений, используйте виртуального!

---

### Декларативность

Декларативные иснтрументы позволяют нам описывать **что мы хотим получить**, в то время как традиционные императивные инструменты
заставляют нас писать **что мы хотим сделать**.

К традиционным императивным библиотекам относятся [aio-pika]({{ urls.aiopika }}){target="_blank"}, [pika]({{ urls.pika }}){target="_blank"}, [redis-py]({{ urls.redis }}){target="_blank"}, [nats-py]({{ urls.nats_py }}){target="_blank"}, [aiokafka]({{ urls.aiokafka }}){target="_blank"} и подобные.

Например, это **Quickstart** из библиотеки *aio-pika*:

```python
import asyncio
import aio_pika

async def main():
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/"
    )

    queue_name = "test_queue"

    async with connection:
        channel = await connection.channel()

        queue = await channel.declare_queue(queue_name)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(message.body)

asyncio.run(main())
```

**aio-pika** - это действительно отличный инструмент с легкой кривой обучения. Но он все еще императивный. Вам необходимо самому объявлять и инициализировать *connect*, *channel*, *queue* и *exchange*. Также, вам нужно управлять контекстом вашего *connection*, *message*, *queue* для того, чтобы избежать возможных проблем с обработкой.

Это не плохой способ написания кода, но он может быть проще.

```python
from propan import PropanApp, RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)

@broker.handle("test_queue")
async def base_handler(body):
    print(body)
```

Это декларативный способ написать тот же код с помощью **Propan**. Разве он не гораздо проще?

При это **Propan** оставляет для вас возможность использовать все низкоуровневые инструменты каждого брокера.

---

## Поддерживаемые брокеры

!!! note "Нужна ваша помощь"
    Фреймоворк сейчас активно развивается. У нас очень длинный список того, что еще предстоит реализовать и различные брокеры - только его часть. Если вы хотите реализовать что-то из этого списка или помочь любым другим способом - загляните [сюда](contributing/1_todo/)

|                   | async                                                   | sync                 |
|-------------------|:-------------------------------------------------------:|:--------------------:|
| **RabbitMQ**      | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag: |
| **Redis**         | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag: |
| **Nats**          | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag: |
| **Kafka**         | :warning: **beta** :warning:                            | :mag: planning :mag: |
| **SQS**           | :warning: **beta** :warning:                            | :mag: planning :mag: |
| **NatsJS**        | :hammer_and_wrench: **in progress** :hammer_and_wrench: | :mag: planning :mag: |
| **MQTT**          | :mag: planning :mag:                                    | :mag: planning :mag: |
| **Redis Streams** | :mag: planning :mag:                                    | :mag: planning :mag: |
| **Pulsar**        | :mag: planning :mag:                                    | :mag: planning :mag: |