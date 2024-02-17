from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TYPE_CHECKING, TypeVar

from .type import (
    BoundingVolumeBoxDictType,
    BoundingVolumeRegionDictType,
    BoundingVolumeSphereDictType,
)
from .root_property import RootProperty

if TYPE_CHECKING:
    from typing_extensions import Self


# @author:wbw
# 定义包围盒泛型类型，可接受三种具体的字典类型
_BoundingVolumeJsonDictT = TypeVar(
    "_BoundingVolumeJsonDictT",
    BoundingVolumeBoxDictType,
    BoundingVolumeRegionDictType,
    BoundingVolumeSphereDictType,
)

#****************************
#   boundingVolume基类
#****************************
class BoundingVolume(
    RootProperty[_BoundingVolumeJsonDictT], Generic[_BoundingVolumeJsonDictT]
): 
    
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    @abstractmethod
    def from_dict(cls, bounding_volume_dict: _BoundingVolumeJsonDictT) -> Self:
        ...

    def is_box(self) -> bool:
        return False

    def is_region(self) -> bool:
        return False

    def is_sphere(self) -> bool:
        return False

    @abstractmethod
    def to_dict(self) -> _BoundingVolumeJsonDictT:
        ...

