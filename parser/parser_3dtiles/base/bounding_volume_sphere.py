from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import numpy.typing as npt

from .type import BoundingVolumeSphereDictType
from .bounding_volume import BoundingVolume

if TYPE_CHECKING:
    from typing_extensions import Self
    from .tile import Tile

np.set_printoptions(linewidth=500)

#***********************************************************
#   Regarding the operation of sphere type in boundingVolume
#***********************************************************
class BoundingVolumeSphere(BoundingVolume[BoundingVolumeSphereDictType]):
    """
    The boundingVolume. sphere property is an array of four numbers used to define a bounding sphere. 
    The first three elements define the x, y, and z values of the center of the sphere in the right-hand 3-axis (x, y, z) Cartesian coordinate system along the z-axis. 
    The last element (index 3) defines the radius in meters
    """
    def __init__(self) -> None:
        super().__init__()
        self._sphere: npt.NDArray[np.float64] | None = None

    @classmethod
    def from_dict(cls, bounding_volume_sphere_dict: BoundingVolumeSphereDictType) -> Self:
        bounding_volume_sphere = cls()
        bounding_volume_sphere.set_from_list(bounding_volume_sphere_dict["sphere"])
        bounding_volume_sphere.set_root_properties_from_dict(bounding_volume_sphere_dict)

        return bounding_volume_sphere


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

    def is_sphere(self) -> bool:
        return True

    def set_from_list(self, sphere_list: npt.ArrayLike) -> None:
        sphere = np.array(sphere_list, dtype=float)

        valid, reason = BoundingVolumeSphere.is_valid(sphere)
        if not valid:
            raise ValueError(reason)
        self._sphere = sphere

    def to_dict(self) -> BoundingVolumeSphereDictType:
        if self._sphere is None:
            raise AttributeError("Bounding Volume Sphere is not defined.")

        dict_data: BoundingVolumeSphereDictType = {"sphere": list(self._sphere)}
        return self.add_root_properties_to_dict(dict_data)

    @staticmethod
    # Check if the sphere is valid
    def is_valid(sphere: npt.NDArray[np.float64]) -> tuple[bool, str]:
        if sphere is None:
            return False, "Bounding Volume Sphere is not defined."
        if sphere.ndim != 1:
            return False, "Bounding Volume Sphere has wrong dimensions."
        if sphere.shape[0] != 4:
            return False, "Warning: Bounding Volume Sphere must have 4 elements."
        return True, ""
