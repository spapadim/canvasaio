import re
import asyncio

from typing import (
    overload,
    Optional, Union, Generic, TypeVar, Type,
    AsyncIterator, AsyncIterable, Awaitable,
    List,
)
from .requester import Requester


T = TypeVar("T")
TS = TypeVar("TS")
class PaginatedList(AsyncIterable[T], Generic[T]):
    """
    Abstracts `pagination of Canvas API \
    <https://canvas.instructure.com/doc/api/file.pagination.html>`_.
    """

    async def _async_getitem_single(self, index: int, fut: asyncio.Future) -> None:
        try:
            await self._get_up_to_index(index)
            fut.set_result(self._elements[index])
        except Exception as e:
            fut.set_exception(e)

    @overload
    def __getitem__(self, index: int) -> Awaitable[T]: pass
    @overload
    def __getitem__(self, index: slice) -> "PaginatedList._Slice[T]": pass

    def __getitem__(self, index):
        assert isinstance(index, (int, slice))
        if isinstance(index, int):
            if index < 0:
                raise IndexError("Cannot negative index a PaginatedList")
            # Based on https://gist.github.com/achimnol/da6983838b31f6f188d539b9ce9ea5ba
            loop = asyncio.get_running_loop()
            fut = loop.create_future()
            loop.create_task(self._async_getitem_single(index, fut))
            return fut
        else:
            return self._Slice(self, index)

    def __init__(
        self,
        content_class: Type[T],
        requester: Requester,
        request_method: str,
        first_url: str,
        extra_attribs: Optional[dict] = None,
        _root=None,
        **kwargs
    ):

        self._elements = list()

        self._requester = requester
        self._content_class = content_class
        self._first_url = first_url
        self._first_params = kwargs or {}
        self._first_params["per_page"] = kwargs.get("per_page", 100)
        self._next_url = first_url
        self._next_params = self._first_params
        self._extra_attribs = extra_attribs or {}
        self._request_method = request_method
        self._root = _root

    async def __aiter__(self) -> AsyncIterator[T]:
        for element in self._elements:
            yield element
        while self._has_next():
            new_elements = await self._grow()
            for element in new_elements:
                yield element

    def __repr__(self) -> str:
        return "<PaginatedList of type {}>".format(self._content_class.__name__)

    async def _get_next_page(self) -> List:
        response = await self._requester.request(
            self._request_method, self._next_url, **self._next_params
        )
        data = await response.json()
        self._next_url = None

        next_link = response.links.get("next")
        regex = r"{}(.*)".format(re.escape(self._requester.base_url))

        self._next_url = (
            re.search(regex, str(next_link["url"])).group(1) if next_link else None
        )

        self._next_params = {}

        content = []

        if self._root:
            try:
                data = data[self._root]
            except KeyError:
                # TODO: Fix this message to make more sense to an end user.
                raise ValueError("Invalid root value specified.")

        # XXX check; cf group.py:1071
        if type(data) == dict:  # XXX playing it safe for now, consider "type(data) != list" later
            data = [data]

        for element in data:
            if element is not None:
                element.update(self._extra_attribs)
                content.append(self._content_class(self._requester, element))

        return content

    async def _get_up_to_index(self, index: int) -> None:
        while len(self._elements) <= index and self._has_next():
            await self._grow()

    async def _grow(self) -> List:
        new_elements = await self._get_next_page()
        self._elements += new_elements
        return new_elements

    def _has_next(self) -> bool:
        return self._next_url is not None

    def _is_larger_than(self, index: int) -> bool:
        return len(self._elements) > index or self._has_next()

    class _Slice(AsyncIterable[TS], Generic[TS]):
        def __init__(self, the_list: 'PaginatedList[TS]', the_slice: slice):
            self._list = the_list
            self._start = the_slice.start or 0
            self._stop = the_slice.stop
            self._step = the_slice.step or 1

            if self._start < 0 or self._stop < 0:
                raise IndexError("Cannot negative index a PaginatedList slice")

        async def __aiter__(self) -> AsyncIterator[TS]:
            index = self._start
            while not self._finished(index):
                if self._list._is_larger_than(index):
                    try:
                        yield (await self._list[index])
                    except IndexError:
                        return
                    index += self._step
                else:
                    return

        def _finished(self, index: int) -> bool:
            return self._stop is not None and index >= self._stop
