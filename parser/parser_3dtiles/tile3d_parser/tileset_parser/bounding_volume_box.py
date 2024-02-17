from __future__ import annotations

from typing import TYPE_CHECKING
import copy
import numpy as np
import numpy.typing as npt

from .type import BoundingVolumeBoxDictType
from .bounding_volume import BoundingVolume
if TYPE_CHECKING:
    from typing_extensions import Self

np.set_printoptions(linewidth=500)

#****************************************
#   关于boundingVolume中Box类型的操作
#****************************************
class BoundingVolumeBox(BoundingVolume[BoundingVolumeBoxDictType]):

    def __init__(self) -> None:
        super().__init__()
        self._box: npt.NDArray[np.float64] | None = None 

    @classmethod
    def from_dict(cls, bounding_volume_box_dict: BoundingVolumeBoxDictType) -> Self:
        bounding_volume_box = cls()
        # 从字典中获取box的值
        bounding_volume_box.set_from_list(bounding_volume_box_dict["box"])
        # 从字典中获取根属性的值
        bounding_volume_box.set_properties_from_dict(bounding_volume_box_dict)

        return bounding_volume_box

    def is_box(self) -> bool:
        return True

    def set_from_list(self, box_list: npt.ArrayLike) -> None:
        # 将box_list转换为numpy数组
        box = np.array(box_list, dtype=float)

        valid, reason = BoundingVolumeBox.is_valid(box)
        if not valid:
            raise ValueError(reason)
        self._box = box


    def to_dict(self) -> BoundingVolumeBoxDictType:
        if self._box is None:
            raise AttributeError("Bounding Volume Box is not defined.")

        dict_data: BoundingVolumeBoxDictType = {"box": list(self._box)}
        return self.add_root_properties_to_dict(dict_data)


    @staticmethod
    def is_valid(box: npt.NDArray[np.float64]) -> tuple[bool, str]:
        if box is None:
            return False, "Bounding Volume Box is not defined."
        if box.ndim != 1:
            return False, "Bounding Volume Box has wrong dimensions."
        if box.shape[0] != 12:
            return False, "Warning: Bounding Volume Box must have 12 elements."
        return True, ""
    


