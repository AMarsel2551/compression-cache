import time, pickle
from zstandard import ZstdCompressor, ZstdDecompressor
from typing import Optional, Callable, List, Any, Union
from inspect import signature, iscoroutinefunction
from typing import Dict, Tuple


class CacheTTL:
    def __init__(self, ttl: float = 60, key_args: Optional[List[str]] = None, compressor_level: Optional[int] = None):
        """ Параметры кэширования """
        self.ttl: float = ttl
        self.key_args: Union[List[str], None] = key_args
        self.compressor_level: Union[int, None] = compressor_level

        """ Внутренние параметры """
        self.data: Any = None
        self.key: Union[Tuple[Any, ...], None] = None
        self.compressor: ZstdCompressor = ZstdCompressor(level=compressor_level or 3)
        self.decompressor: ZstdDecompressor = ZstdDecompressor()
        self.cache: Dict[Tuple[Any, ...], Any] = {}
        self.timestamps: Dict[Tuple[Any, ...], float] = {}

    def __call__(self, func: Callable, *args, **kwargs) -> Callable:
        self.func = func

        # For synchronous functions
        if iscoroutinefunction(self.func):
            async def wrapper(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Any:
                self.data = self.checking_the_cache(*args, **kwargs)
                if self.data:
                    return self.data

                self.data = await func(*args, **kwargs)
                return self.saving_the_cache()

            return wrapper

        # For asynchronous functions
        else:
            def wrapper(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Any:
                self.data = self.checking_the_cache(*args, **kwargs)
                if self.data:
                    return self.data

                self.data = func(*args, **kwargs)
                return self.saving_the_cache()

            return wrapper

    def checking_the_cache(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Any:
        self.key = self.generate_key(*args, **kwargs)
        if self.key in self.cache and time.time() - self.timestamps[self.key] < self.ttl:
            self.data = self.cache[self.key]
            if self.compressor_level:
                self.decompress_data()
            return self.data
        return None

    def saving_the_cache(self) -> Any:
        if self.compressor_level:
            self.compress_data()
        self.cache[self.key] = self.data
        self.timestamps[self.key] = time.time()
        return self.data

    def make_hashable(self, value: Any) -> Any:
        """ Преобразует значение в хэшируемый формат """
        if isinstance(value, dict):
            return tuple(sorted((k, self.make_hashable(v)) for k, v in value.items()))
        if isinstance(value, list):
            return tuple(self.make_hashable(v) for v in value)
        if hasattr(value, "__dict__"):  # Преобразуем объект с атрибутами
            return tuple(sorted((k, self.make_hashable(v)) for k, v in vars(value).items()))
        return value

    def generate_key(self, *args, **kwargs) -> Tuple[Any, ...]:
        """ Генерирует ключ для кеша на основе указанных аргументов """
        sig = signature(self.func)
        bound_args = sig.bind(*args, **kwargs)

        bound_args.apply_defaults()

        if self.key_args is None:
            return tuple(sorted((k, self.make_hashable(value=value)) for k, value in bound_args.arguments.items()))

        key = {
            arg_name: self.make_hashable(value=bound_args.arguments[arg_name])
            for arg_name in self.key_args
            if arg_name in bound_args.arguments
        }
        return tuple(sorted(key.items()))

    def compress_data(self) -> None:
        """ Сжатие кэшированного обьекта """
        self.data = self.compressor.compress(pickle.dumps(self.data))

    def decompress_data(self) -> None:
        """ Распаковывания кэшированного обьекта """
        self.data = pickle.loads(self.decompressor.decompress(self.data))

