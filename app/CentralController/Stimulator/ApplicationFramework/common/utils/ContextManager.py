from typing import Union, Callable

from injector import Injector, Provider, T, singleton


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class ContextManager:
    context_injector: Injector = None

    @classmethod
    def initial(cls):
        cls.context_injector = Injector()

    @classmethod
    def set_context_injector(cls, context_injector: Injector):
        cls.context_injector = context_injector

    @classmethod
    def get_context_injector(cls) -> Injector:
        return cls.context_injector

    @classmethod
    def bind_class(cls, clazz: type, to_target: Union[None, T, Callable[..., T], Provider[T]]) -> None:
        context_injector = cls.context_injector.create_child_injector()
        context_injector.binder.bind(clazz, to=to_target, scope=singleton)
        cls.context_injector = context_injector

    @classmethod
    def get_instance(cls, clazz: type) -> any:
        return cls.context_injector.get(clazz)
