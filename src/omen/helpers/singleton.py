from abc import ABCMeta


class Singleton(type):
    """Singleton metaclass for implementing singleton patterns. 
    Source: https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

    Usage:
    ```
    class MySingleInstanceClass(metaclass=Singleton): ...
    ```
    """
    instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances:
            cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]