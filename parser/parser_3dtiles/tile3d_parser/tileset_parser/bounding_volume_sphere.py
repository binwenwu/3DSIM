from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from .type import BoundingVolumeSphereDictType
from .bounding_volume import BoundingVolume

if TYPE_CHECKING:
    from typing_extensions import Self

np.set_printoptions(linewidth=500)

#****************************************
#   关于boundingVolume中sphere类型的操作
#****************************************
class BoundingVolumeSphere(BoundingVolume[BoundingVolumeSphereDictType]):

    def __init__(self) -> None:
        super().__init__()
        self._sphere: npt.NDArray[np.float64] | None = None

    @classmethod
    # 从字典中返回sphere类型的boundingVolume
    def from_dict(cls, bounding_volume_sphere_dict: BoundingVolumeSphereDictType) -> Self:
        bounding_volume_sphere = cls()
        bounding_volume_sphere.set_from_list(bounding_volume_sphere_dict["sphere"])

        bounding_volume_sphere.set_properties_from_dict(bounding_volume_sphere_dict)

        return bounding_volume_sphere

    # 判断boundingVoume的类型是否为sphere
    def is_sphere(self) -> bool:
        return True

    # 从字符串中返回sphere
    def set_from_list(self, sphere_list: npt.ArrayLike) -> None:
        sphere = np.array(sphere_list, dtype=float)

        valid, reason = BoundingVolumeSphere.is_valid(sphere)
        if not valid:
            raise ValueError(reason)
        self._sphere = sphere

    # 将sphere类型的boundingVolume输出为字典
    def to_dict(self) -> BoundingVolumeSphereDictType:
        if self._sphere is None:
            raise AttributeError("Bounding Volume Sphere is not defined.")

        dict_data: BoundingVolumeSphereDictType = {"sphere": list(self._sphere)}
        return self.add_root_properties_to_dict(dict_data)

    @staticmethod
    # 判断是否为正确的sphere
    def is_valid(sphere: npt.NDArray[np.float64]) -> tuple[bool, str]:
        if sphere is None:
            return False, "Bounding Volume Sphere is not defined."
        if sphere.ndim != 1:
            return False, "Bounding Volume Sphere has wrong dimensions."
        if sphere.shape[0] != 4:
            return False, "Warning: Bounding Volume Sphere must have 4 elements."
        return True, ""
