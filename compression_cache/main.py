import pickle
import time
import os
import redis
from inspect import iscoroutinefunction, signature
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union
import ujson
from zstandard import ZstdCompressor, ZstdDecompressor

from compression_cache.models import EnableIgnore, StoragePlaces, Empty, Cache, Key


class CacheTTL:
    def __init__(
            self,
            ttl: float = 60,
            key_args: Optional[List[str]] = None,
            compressor_level: Optional[int] = None,
            enable_ignore_res: Optional[EnableIgnore] = None,
            ignore_values_res: Optional[Tuple[Any, ...]] = None,
            storage_places: StoragePlaces = StoragePlaces.LOCAL,
            shared: bool = False,
            external_topic: Optional[str] = None,
            external_key: Optional[str] = None,
    ) -> None:
        """Параметры кэширования"""
        self.ttl: int = ttl
        self.key_args: Union[List[str], None] = key_args
        self.compressor_level: Union[int, None] = compressor_level
        self.enable_ignore_res = enable_ignore_res
        self.ignore_values_res = ignore_values_res
        self.storage_places = storage_places
        self.shared = shared
        self.external_topic = external_topic
        self.external_key = external_key

        """Внутренние параметры"""
        self.data: Any = None
        self.key: Optional[str] = None
        self.compressor: ZstdCompressor = ZstdCompressor(level=compressor_level or 3)
        self.decompressor: ZstdDecompressor = ZstdDecompressor()
        self.cache: Dict[str, Cache] = {}
        self.recording_time = None

        self.example_params()


    def __call__(
        self, func: Callable[..., Any], *args: Tuple[Any], **kwargs: Dict[str, Any]
    ) -> Union[Callable[..., Any], Awaitable[Any]]:
        self.func = func

        def wrapper(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Any:
            """Рабочая функция"""

            # Очистка устаревших элементов
            self.clear_expired_cache()
            self.data = None

            # Async
            if iscoroutinefunction(self.func):

                async def async_func(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Any:
                    self.data = self.checking_the_cache(*args, **kwargs)
                    if not isinstance(self.data, Empty):
                        return self.data

                    self.data = await func(*args, **kwargs)

                    return self.saving_the_cache()

                return async_func(*args, **kwargs)

            # Sync
            else:
                self.data = self.checking_the_cache(*args, **kwargs)
                if not isinstance(self.data, Empty):
                    return self.data

                self.data = func(*args, **kwargs)
                return self.saving_the_cache()

        return wrapper


    def example_params(self):
        if self.shared:
            if self.storage_places == StoragePlaces.LOCAL:
                raise "In local mode, you cannot open access to the cache! storage_places != LOCAL"

            if self.external_topic is None or self.external_key is None:
                raise "external_topic or external_key is None"

        if self.storage_places == StoragePlaces.REDIS:
            if self.compressor_level:
                raise "You can't use data compression when working with redis!"

    def checking_the_cache(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Union[Any, Empty]:
        """Проверяем кеш"""
        self.key = self.generate_key(*args, **kwargs)

        if self.key in self.cache:
            if self.cache[self.key].storage_places == StoragePlaces.REDIS:
                self.get_redis()

            else:
                self.get_local()

            if self.compressor_level:
                self.decompress_data()

            return self.data

        return Empty()

    def get_external_key(self):
        return f"{self.external_topic}_{self.external_key}"

    def generate_key(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> str:
        """Генерирует ключ для кеша на основе указанных аргументов"""
        sig = signature(self.func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        args = []
        if self.key_args:
            v_args = bound_args.arguments
            for key in v_args:
                if key in self.key_args:
                    args.append(v_args[key])

        key = Key(
            id_func=id(self.func),
            name_func=self.func.__name__,
            args=tuple(args)
        )
        return str(hash(str(key)))


    def get_local(self) -> None:
        self.data = self.cache[self.key].data
        return None

    def saving_local(self) -> None:
        self.recording_time = time.time()
        self.cache[self.key] = Cache(
            internal_key=self.key,
            data=self.data,
            storage_places=StoragePlaces.LOCAL,
            recording_time=self.recording_time,
            time_of_death=self.recording_time - self.ttl
        )
        return None


    def get_connection_redis(self) -> redis.StrictRedis:
        return redis.StrictRedis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=os.getenv("REDIS_PORT", 6379),
            username=os.getenv("REDIS_USERNAME", "default"),
            password=os.getenv("REDIS_PASSWORD", ""),
            db=os.getenv("REDIS_DB", 0),
            decode_responses=True
        )

    def get_redis(self) -> None:
        connection = self.get_connection_redis()
        res = connection.get(self.get_external_key())

        if res is None:
            self.data = Empty()

        else:
            self.data = ujson.loads(res)

        return None

    def saving_redis(self) -> None:
        self.recording_time = time.time()
        self.cache[self.key] = Cache(
            internal_key=self.key,
            external_key=self.get_external_key(),
            data=None,
            storage_places=StoragePlaces.REDIS,
            recording_time=self.recording_time,
            time_of_death=self.recording_time - self.ttl
        )
        connection = self.get_connection_redis()
        connection.setex(self.get_external_key(), self.ttl, ujson.dumps(self.data, default=str))
        return None


    def saving_the_cache(self) -> Any:
        """Сохраняем кеш"""
        # Проверяем игнорируемые результаты, и не сохраняем их если включен параметр <enable_ignore_res>
        if self.enable_ignore_res:
            if self.enable_ignore_res == EnableIgnore.TYPE:
                if isinstance(self.data, self.ignore_values_res):
                    return self.data

            elif self.enable_ignore_res == EnableIgnore.VALUE:
                if self.data in self.ignore_values_res:
                    return self.data

        # Сжатие данных
        if self.compressor_level:
            self.compress_data()

        # Сохранение данных
        if self.key:
            if self.storage_places == StoragePlaces.REDIS:
                self.saving_redis()

            else:
                self.saving_local()

        # Восстановление данных
        if self.compressor_level:
            self.decompress_data()
        return self.data

    def clear_expired_cache(self) -> None:
        """Удаляет устаревшие записи из кеша"""
        current_time = time.time()
        data_list = [self.cache[key] for key in self.cache if current_time < self.cache[key].time_of_death]
        for data in data_list:
            if data.storage_places == StoragePlaces.REDIS:
                self.cache.pop(data.internal_key, None)

            else:
                self.cache.pop(data.internal_key, None)


    def compress_data(self) -> None:
        """Сжатие кэшированного объекта"""
        self.data = self.compressor.compress(pickle.dumps(self.data))

    def decompress_data(self) -> None:
        """Распаковывание кэшированного объекта"""
        self.data = pickle.loads(self.decompressor.decompress(self.data))
