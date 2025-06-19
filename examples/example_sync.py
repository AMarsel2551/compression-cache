import faker, random
from typing import Dict, List, Union
from compression_cache import CacheTTL
from compression_cache.main import StoragePlaces


def get_accounts(count_account: int) -> List[Dict[str, Union[str, int]]]:
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


@CacheTTL(ttl=5, key_args=["count_account"], compressor_level=None, storage_places=StoragePlaces.LOCAL)
def sync_function(count_account: int) -> List[Dict[str, Union[str, int]]]:
    print("call func")
    return get_accounts(count_account=count_account)


def main():
    for count_account in [10, 20, 10, 20]:
        res = sync_function(count_account=count_account)
        print(f"{count_account=} / {res=}")


main()
