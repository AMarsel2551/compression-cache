import asyncio
from typing import Dict, List, Union

from cache import CacheTTL
from examples.accounts import get_accounts


@CacheTTL(ttl=60 * 5, key_args=["count_account"], compressor_level=3)
async def async_function(count_account: int) -> List[Dict[str, Union[str, int]]]:
    return get_accounts(count_account=count_account)


for count_account in [10, 20, 10, 20]:
    print(f"a: {count_account}")
    asyncio.run(async_function(count_account=count_account))  # type: ignore
