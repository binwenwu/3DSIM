from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from .type import BoundingVolumeRegionDictType
from .bounding_volume import BoundingVolume

if TYPE_CHECKING:
    from typing_extensions import Self

np.set_printoptions(linewidth=500)

#****************************************
#   关于boundingVolume中Region类型的操作
#****************************************
class BoundingVolumeRegion(BoundingVolume[BoundingVolumeRegionDictType]):

    def __init__(self) -> None:
        super().__init__()
        self._region: npt.NDArray[np.float64] | None = None

    @classmethod
    # 从字典中返回region类型的boundingVolume
    def from_dict(cls, bounding_volume_region_dict: BoundingVolumeRegionDictType) -> Self:
        bounding_volume_region = cls()
        bounding_volume_region.set_from_list(bounding_volume_region_dict["region"])

        bounding_volume_region.set_properties_from_dict(bounding_volume_region_dict)

        return bounding_volume_region
    
    # 判断boundingVoume的类型是否为region
    def is_region(self) -> bool:
        return True

    # 从字符串中返回region
    def set_from_list(self, region_list: npt.ArrayLike) -> None:
        region = np.array(region_list, dtype=float)

        valid, reason = BoundingVolumeRegion.is_valid(region)
        if not valid:
            raise ValueError(reason)
        self._region = region

    # 将region类型的boundingVolume输出为字典
    def to_dict(self) -> BoundingVolumeRegionDictType:
        if self._region is None:
            raise AttributeError("Bounding Volume Region is not defined.")

        dict_data: BoundingVolumeRegionDictType = {"region": list(self._region)}
        return self.add_root_properties_to_dict(dict_data)

    @staticmethod
    # 判断是否为正确的region
    def is_valid(region: npt.NDArray[np.float64]) -> tuple[bool, str]:
        if region is None:
            return False, "Bounding Volume Region is not defined."
        if region.ndim != 1:
            return False, "Bounding Volume Region has wrong dimensions."
        if region.shape[0] != 6:
            return False, "Warning: Bounding Volume Region must have 4 elements."
        return True, ""
