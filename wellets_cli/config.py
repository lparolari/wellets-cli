import logging
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


class Config(Generic[T]):
    def __init__(
        self,
        key: str,
        value: Optional[T] = None,
        description: Optional[str] = None,
        settable: Optional[bool] = None,
        server_side: Optional[bool] = None,
        sensitive: Optional[bool] = None,
        getter: Optional[Any] = None,
        setter: Optional[Any] = None,
    ):
        self._key = key
        self._value = value
        self._description = description
        self._settable = settable
        self._server_side = server_side
        self._sensitive = sensitive
        self._getter = getter
        if setter is False:
            self._setter = lambda config, _1, _2: logging.warning(
                f"The config '{config.key()}' tried to set a value using the `set_value()` method, but this is currently disabled. If this was intended, please implement the config setter."
            )
        if setter is not None:
            self._settable = True
            self._setter = setter

    def value(self, **kwargs) -> T:
        if self._getter:
            return self._getter(self, **kwargs)

        return self._value

    def set_value(self, value, **kwargs) -> T:
        if not self.is_settable():
            raise ValueError(f"Config '{self.key()}' is not settable")

        if self._setter:
            return self._setter(self, value, **kwargs)

        self._value = value
        return value

    def key(self) -> str:
        return self._key

    def description(self) -> str:
        return self._description

    def is_settable(self) -> bool:
        return self._settable or False

    def is_server_side(self) -> bool:
        return self._server_side or False

    def is_sensitive(self) -> bool:
        return self._sensitive or False

    def __repr__(self):
        return f"Config(key={self._key}, value={self._value})"

    def __str__(self):
        return "<sensitive>" if self.is_sensitive() else str(self.value())


class ConfigManager:
    _configs = []

    @classmethod
    def add_config(cls, config: Config):
        cls._configs.append(config)

    @classmethod
    def add_configs(cls, configs: List[Config]):
        cls._configs.extend(configs)

    @classmethod
    def clear(cls):
        cls._configs = []

    @classmethod
    def has_key(cls, key):
        return key in cls.keys()

    @classmethod
    def keys(cls, server_side=None, settable=None):
        def cond(c):
            return all(
                [
                    server_side is None or c.is_server_side() == server_side,
                    settable is None or c.is_settable() == settable,
                ]
            )

        return [config.key() for config in cls._configs if cond(config)]

    @classmethod
    def get(cls, key, throw=True):
        if not cls.has_key(key):
            if throw:
                raise ValueError(f"Config '{key}' does not exist")
            return None
        return cls.config(key).value()

    @classmethod
    def configs(cls, keys=[]):
        return [
            config for config in cls._configs if len(keys) == 0 or config.key() in keys
        ]

    @classmethod
    def config(cls, key) -> Optional[Config]:
        configs = cls.configs(keys=[key])

        if len(configs) == 0:
            return None

        return configs[0]
