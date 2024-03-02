from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import numpy.typing as npt

from .type import BoundingVolumeRegionDictType
from .bounding_volume import BoundingVolume

if TYPE_CHECKING:
    from typing_extensions import Self
    from .tile import Tile

np.set_printoptions(linewidth=500)

#*******************************************************
#   About the Operation of Region Type in BoundingVolume
#*******************************************************
class BoundingVolumeRegion(BoundingVolume[BoundingVolumeRegionDictType]):
    """
    The boundingVolume. region property is an array of six numbers 
    that define boundary geographic regions using latitude, longitude, and height coordinates, 
    in the order of [west, south, east, north, minimum height, maximum height]
    """

    def __init__(self) -> None:
        super().__init__()
        self._region: npt.NDArray[np.float64] | None = None

    @classmethod
    def from_dict(cls, bounding_volume_region_dict: BoundingVolumeRegionDictType) -> Self:
        bounding_volume_region = cls()
        bounding_volume_region.set_from_list(bounding_volume_region_dict["region"])
        bounding_volume_region.set_root_properties_from_dict(bounding_volume_region_dict)

        return bounding_volume_region
    

    def get_center(self) -> npt.NDArray[np.float64]:
        pass
    

    def translate(self, offset: npt.NDArray[np.float64]) -> None:
        pass


    def transform(self, transform: npt.NDArray[np.float64]) -> None:
        pass


    def add(self, other: BoundingVolume[Any]) -> None:
        pass


    def sync_with_children(self, owner: Tile) -> None:
        pass


    def is_region(self) -> bool:
        return True

    def set_from_list(self, region_list: npt.ArrayLike) -> None:
        region = np.array(region_list, dtype=float)

        valid, reason = BoundingVolumeRegion.is_valid(region)
        if not valid:
            raise ValueError(reason)
        self._region = region

    def to_dict(self) -> BoundingVolumeRegionDictType:
        if self._region is None:
            raise AttributeError("Bounding Volume Region is not defined.")

        dict_data: BoundingVolumeRegionDictType = {"region": list(self._region)}
        return self.add_root_properties_to_dict(dict_data)

    @staticmethod
    def is_valid(region: npt.NDArray[np.float64]) -> tuple[bool, str]:
        if region is None:
            return False, "Bounding Volume Region is not defined."
        if region.ndim != 1:
            return False, "Bounding Volume Region has wrong dimensions."
        if region.shape[0] != 6:
            return False, "Warning: Bounding Volume Region must have 4 elements."
        return True, ""
