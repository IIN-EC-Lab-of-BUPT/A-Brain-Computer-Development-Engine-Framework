import threading
from functools import wraps


def singleton(cls):
    instances = {}
    # 创建一个全局的锁对象，用于线程安全
    lock = threading.Lock()

    @wraps(cls)
    def wrapper(*args, **kwargs):
        # 使用lock确保线程安全
        with lock:
            # 检查实例是否存在，如果不存在则创建
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)

        # 返回已有的或新创建的实例
        return instances[cls]

    # 添加文档字符串说明，增强可维护性
    wrapper.__doc__ = """
    Singleton装饰器，用于确保一个类只有一个实例。

    使用方法：
    请将此装饰器应用于期望作为单例实例的类之前。
    例如：
    @singleton
    class MySingleton:
        pass

    注意事项：
    - 这个实现是线程安全的。
    - 实例化参数的变化不会影响到已有的单例实例。
    """

    return wrapper
