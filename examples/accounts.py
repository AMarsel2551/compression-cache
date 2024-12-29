import random
from typing import Dict, List, Union

import faker


def get_accounts(count_account: int) -> List[Dict[str, Union[str, int]]]:
    print("Get accounts")
    fake = faker.Faker()
    accounts: List[Dict[str, Union[str, int]]] = []
    for _ in range(count_account):
        account = {
            "id": random.randint(1000, 9999),
            "name": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
        }
        accounts.append(account)
    return accounts
