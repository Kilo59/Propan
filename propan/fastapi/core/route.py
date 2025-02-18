import asyncio
import inspect
from itertools import dropwhile
from typing import Any, Callable, Coroutine, Optional

from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import get_dependant, solve_dependencies
from fastapi.routing import run_endpoint_function
from pydantic import ValidationError, create_model
from starlette.requests import Request
from starlette.routing import BaseRoute

from propan.brokers._model import BrokerUsecase
from propan.brokers._model.schemas import PropanMessage as NativeMessage
from propan.types import AnyDict


class PropanRoute(BaseRoute):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        broker: BrokerUsecase,
        *,
        dependency_overrides_provider: Optional[Any] = None,
        **handle_kwargs: AnyDict,
    ) -> None:
        self.path = path
        self.broker = broker
        self.dependant = get_dependant(path=path, call=endpoint)

        handler = PropanMessage.get_session(
            self.dependant, dependency_overrides_provider
        )
        broker.handle(path, _raw=True, **handle_kwargs)(handler)  # type: ignore


class PropanMessage(Request):
    scope: AnyDict
    _cookies: AnyDict
    _headers: AnyDict  # type: ignore
    _body: AnyDict  # type: ignore
    _query_params: AnyDict  # type: ignore

    def __init__(
        self,
        body: Optional[AnyDict] = None,
        headers: Optional[AnyDict] = None,
    ):
        self.scope = {}
        self._cookies = {}
        self._headers = headers or {}
        self._body = body or {}
        self._query_params = self._body

    @classmethod
    def get_session(
        cls,
        dependant: Dependant,
        dependency_overrides_provider: Optional[Any] = None,
    ) -> Callable[[NativeMessage], Any]:
        assert dependant.call
        func = get_app(dependant, dependency_overrides_provider)

        dependencies_names = tuple(i.name for i in dependant.dependencies)

        first_arg = next(
            dropwhile(
                lambda i: i in dependencies_names,
                inspect.signature(dependant.call).parameters,
            ),
            None,
        )

        async def app(message: NativeMessage) -> Any:
            body = message.decoded_body
            if first_arg is not None:
                if not isinstance(body, dict):  # pragma: no branch
                    body = {first_arg: body}

                session = cls(body, message.headers)
            else:
                session = cls()
            return await func(session)

        return app


def get_app(
    dependant: Dependant,
    dependency_overrides_provider: Optional[Any] = None,
) -> Callable[[PropanMessage], Coroutine[Any, Any, Any]]:
    async def app(request: PropanMessage) -> Any:
        solved_result = await solve_dependencies(
            request=request,
            body=request._body,
            dependant=dependant,
            dependency_overrides_provider=dependency_overrides_provider,
        )

        values, errors, _, _2, _3 = solved_result
        if errors:
            raise ValidationError(errors, create_model("PropanRoute"))

        return await run_endpoint_function(
            dependant=dependant,
            values=values,
            is_coroutine=asyncio.iscoroutinefunction(dependant.call),
        )

    return app
