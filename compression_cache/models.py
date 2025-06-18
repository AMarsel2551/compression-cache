from enum import Enum
from typing import Optional, Any, Tuple

from pydantic import BaseModel, Field


class Empty:
    pass


class EnableIgnore(str, Enum):
    TYPE = "type"
    VALUE = "value"


class StoragePlaces(str, Enum):
    LOCAL = "local"
    REDIS = "redis"


class Cache(BaseModel):
    internal_key: str = Field(..., title="Internal Key")
    external_topic: Optional[str] = Field(default=None, title="External Topic")
    external_key: Optional[str] = Field(default=None, title="External Key")
    data: Optional[Any] = Field(default=None, title="Value")
    storage_places: StoragePlaces = Field(default=StoragePlaces.LOCAL, title="Storage Places")
    recording_time: float = Field(..., title="Recording Time")
    time_of_death: float = Field(..., title="Time Of Death")


class Key(BaseModel):
    id_func: int = Field(..., title="ID Function")
    name_func: str = Field(..., title="Name Function")
    args: Tuple[Any, ...] = Field(..., title="Arguments")