import pickle
import time
from inspect import iscoroutinefunction, signature
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union
from zstandard import ZstdCompressor, ZstdDecompressor


class CacheTTL:
    def __init__(self, ttl: float = 60, key_args: Optional[List[str]] = None, compressor_level: Optional[int] = None) -> None:
        """Параметры кэширования"""
        self.ttl: float = ttl
        self.key_args: Union[List[str], None] = key_args
        self.compressor_level: Union[int, None] = compressor_level

        """ Внутренние параметры """
        self.data: Any = None
        self.key: Union[int, None] = None
        self.compressor: ZstdCompressor = ZstdCompressor(level=compressor_level or 3)
        self.decompressor: ZstdDecompressor = ZstdDecompressor()
        self.cache: Dict[int, Any] = {}
        self.timestamps: Dict[int, float] = {}

    def __call__(
        self, func: Callable[..., Any], *args: Tuple[Any], **kwargs: Dict[str, Any]
    ) -> Union[Callable[..., Any], Awaitable[Any]]:
        # Очистка устаревших элементов
        self.clear_expired_cache()

        self.func = func

        def wrapper(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Any:
            if iscoroutinefunction(self.func):

                async def async_func(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Any:
                    self.data = self.checking_the_cache(*args, **kwargs)
                    if self.data:
                        return self.data

                    self.data = await func(*args, **kwargs)
                    return self.saving_the_cache()

                return async_func(*args, **kwargs)

            else:
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
        if self.key:
            self.cache[self.key] = self.data
            self.timestamps[self.key] = time.time()
        if self.compressor_level:
            self.decompress_data()
        return self.data

    def clear_expired_cache(self) -> None:
        """Удаляет устаревшие записи из кеша"""
        current_time = time.time()
        expired_keys = [key for key, timestamp in self.timestamps.items() if current_time - timestamp >= self.ttl]
        for key in expired_keys:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)

    def generate_key(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> int:
        """Генерирует ключ для кеша на основе указанных аргументов"""
        sig = signature(self.func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        func_id = id(self.func)

        hash_str = f"{func_id}_"
        if self.key_args:
            v_args = bound_args.arguments
            for key in v_args:
                if key in self.key_args:
                    hash_str += str(v_args[key])
        return hash(hash_str)

    def compress_data(self) -> None:
        """Сжатие кэшированного объекта"""
        self.data = self.compressor.compress(pickle.dumps(self.data))

    def decompress_data(self) -> None:
        """Распаковывание кэшированного объекта"""
        self.data = pickle.loads(self.decompressor.decompress(self.data))
