from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TYPE_CHECKING, TypeVar, Any

import numpy as np
import numpy.typing as npt

from .type import (
    BoundingVolumeBoxDictType,
    BoundingVolumeRegionDictType,
    BoundingVolumeSphereDictType,
)
from .root_property import RootProperty

if TYPE_CHECKING:
    from typing_extensions import Self
    from .tile import Tile


"""
Define the bounding box generic type, 
which can accept three specific dictionary types
"""
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
    def get_center(self) -> npt.NDArray[np.float64]:
        ...

    @abstractmethod
    def translate(self, offset: npt.NDArray[np.float64]) -> None:
        ...

    @abstractmethod
    def transform(self, transform: npt.NDArray[np.float64]) -> None:
        ...

    @abstractmethod
    def add(self, other: BoundingVolume[Any]) -> None:
        ...

    @abstractmethod
    def sync_with_children(self, owner: Tile) -> None:
        ...

    @abstractmethod
    def to_dict(self) -> _BoundingVolumeJsonDictT:
        ...

