from typing import Callable, Union, Awaitable
import asyncio


class EventManager:
    """
    事件管理器,负责事件订阅和通知。

    """

    def __init__(self):
        self.__subscribers: dict[str, list[Union[Callable[..., None], Awaitable[None]]]] = {}

    def subscribe(self, event_name: str, callback: Union[Callable[..., None], Awaitable[None]]) -> bool:
        """
        订阅指定事件，添加回调处理逻辑。

        支持的`callback`类型包括：
        - 同步函数（无返回值）。
        - 异步函数（使用`async def`定义）。
        - 实现了无参数异步`execute`方法的异步可执行类的实例。
        - 实现了无参数同步`execute`方法的同步可执行类的实例。

        :param event_name: 事件的唯一标识符，字符串类型，不能为空。
        :param callback: 事件触发时调用的处理逻辑，可以是上述四种类型之一。
        :return: 如果订阅成功，返回True；如果`event_name`为空，则抛出异常。
        """
        if not event_name:
            raise ValueError("event_name cannot be empty or None")

        if event_name not in self.__subscribers:
            self.__subscribers[event_name] = []
        self.__subscribers[event_name].append(callback)

        return True

    def unsubscribe(self, event_name: str, callback: Union[Callable[..., None], Awaitable[None]]) -> bool:
        """
        取消订阅指定事件，删除回调处理逻辑。
        :param event_name: 事件的唯一标识符，字符串类型，不能为空。
        :param callback: 事件触发时调用的处理逻辑，可以是上述四种类型之一。
        :return: 如果取消订阅成功，返回True；如果`event_name`为空，则抛出异常。
        """
        if not event_name:
            raise ValueError("event_name cannot be empty or None")
        if event_name in self.__subscribers:
            if callback in self.__subscribers[event_name]:
                self.__subscribers[event_name].remove(callback)
                return True
            else:
                return False

    @staticmethod
    async def _run_callback(callback: Union[Callable[..., None], Awaitable[None]], *args, **kwargs):
        if asyncio.iscoroutinefunction(callback):
            await callback(*args, **kwargs)
        elif hasattr(callback, '__call__'):  # Check if the callback is an instance method
            if asyncio.iscoroutinefunction(getattr(callback, '__call__', None)):  # Check if the method is asynchronous
                await callback(*args, **kwargs)  # Call the asynchronous method
            else:
                callback(*args, **kwargs)  # Call the synchronous method
        else:
            callback(*args, **kwargs)  # Call the non-callable or non-asynchronous object

    async def notify(self, event_name: str, *args, **kwargs):
        if not event_name:
            raise ValueError("event_name cannot be empty or None")
        if event_name in self.__subscribers:
            tasks = []
            for callback in self.__subscribers[event_name]:
                task = asyncio.create_task(self._run_callback(callback, *args, **kwargs))
                tasks.append(task)

            # Wait for all tasks to complete
            await asyncio.gather(*tasks)

    async def notify_all(self, *args, **kwargs):
        tasks = []
        for event_name, callbacks in self.__subscribers.items():
            for callback in callbacks:
                task = asyncio.create_task(self._run_callback(callback, *args, **kwargs))
                tasks.append(task)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
