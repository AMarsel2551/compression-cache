# COMPRESSION-CACHE


[![AsyncPG Version](https://img.shields.io/pypi/v/compression-cache.svg)](https://pypi.python.org/pypi/compression-cache)


## Установка
1. Установка библиотеки:
   ```bash
   pip install compression-cache

## Примеры:

### Async:
Пример асинхронного кэширования можно найти в [файле](https://github.com/AMarsel2551/compression-cache/blob/main/examples/example_async.py)
   ```python
import asyncio, faker, random
from typing import Dict, List, Union
from compression_cache import CacheTTL


async def get_accounts(count_account: int) -> List[Dict[str, Union[str, int]]]:
    print(f"Get new list accounts count_account: {count_account}")
    fake = faker.Faker()
    accounts: List[Dict[str, Union[str, int]]] = []
    for _ in range(count_account):
        account = {
            "id": random.randint(1000, 9999),
            "name": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
        }
        accounts.append(account) # type: ignore
    return accounts


@CacheTTL(ttl=60 * 5, key_args=["count_account"], compressor_level=3)
async def async_function(count_account: int) -> List[Dict[str, Union[str, int]]]:
    return await get_accounts(count_account=count_account)


async def main():
    for count_account in [10, 20, 10, 20]:
        print(f"count_account: {count_account}")
        await async_function(count_account=count_account)


asyncio.run(main())

   ```


### Sync:
Пример синхронного кэширования можно найти в [файле](https://github.com/AMarsel2551/compression-cache/blob/main/examples/example_sync.py)
   ```python
import faker, random
from typing import Dict, List, Union
from compression_cache import CacheTTL


def get_accounts(count_account: int) -> List[Dict[str, Union[str, int]]]:
    print(f"Get new list accounts count_account: {count_account}")
    fake = faker.Faker()
    accounts: List[Dict[str, Union[str, int]]] = []
    for _ in range(count_account):
        account = {
            "id": random.randint(1000, 9999),
            "name": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
        }
        accounts.append(account) # type: ignore
    return accounts


@CacheTTL(ttl=60 * 5, key_args=["count_account"], compressor_level=3)
def async_function(count_account: int) -> List[Dict[str, Union[str, int]]]:
    return get_accounts(count_account=count_account)


def main():
    for count_account in [10, 20, 10, 20]:
        print(f"count_account: {count_account}")
        async_function(count_account=count_account)


main()

```