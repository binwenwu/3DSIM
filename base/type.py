import numpy as np
from enum import Enum

DEFAULT_TRANSFORMATION = np.identity(4, dtype=np.float64)

class BoundingVolumeType(Enum):
    AABB = "AABB"
    OBB = "OBB"
    Sphere = "Sphere"

class RangeMode(Enum):
    DISTANCE_FROM_EYE_POINT = "DISTANCE"
    PIXEL_SIZE_ON_SCREEN  = "PIXEL"
    GEOMETRIC_ERROR = "GE"

class ModelAsset(Enum):
    POINTCLOUD = "POINTCLOUD"
    PHYSICALFIELD  = "PHYSICALFIELD"
    RASTERRELIEF = "RASTERRELIEF"
    MESH = "MESH"

class ReliefType(Enum):
    GEOTIFF = "GEOTIFF"
    JPG = "JPG"
    PNG = "PNG"

class PointCloudType(Enum):
    XYZ = "XYZ"
    LAS = "LAS"
    LAZ = "LAZ"

class PhysicalFieldType(Enum):
    NETCDF = "NETCDF"
    HDF = "HDF"

class Transform:
    def __init__(self, matrix: np.ndarray):
        if matrix is not None and matrix.shape != (4, 4):
            raise ValueError("Invalid matrix shape. Expected (4, 4).")

        self.matrix = matrix

    def to_dict(self) -> dict:
        if np.array_equal(self.matrix, DEFAULT_TRANSFORMATION):
            return {"transform": []}
        else:
            return {"transform": np.ravel(self.matrix).tolist()}

    @classmethod
    def from_dict(cls, data: dict) -> 'Transform':
        if "transform" not in data:
            raise ValueError("Missing transform data.")
        if not data["transform"]:
            return cls(None)
        if len(data["transform"]) != 16:
            raise ValueError("transform != 16")
        matrix = np.array(data["transform"]).reshape(4, 4)
        return cls(matrix)
    
    @classmethod
    def from_dict_worldT(cls, data: dict) -> 'Transform':
        if "transformToWorld" not in data:
            raise ValueError("Missing transformToWorld data.")
        if not data["transformToWorld"]:
            return cls(None)
        if len(data["transformToWorld"]) != 16:
            raise ValueError("transformToWorld != 16")
        matrix = np.array(data["transformToWorld"]).reshape(4, 4)
        return cls(matrix)
    
    @classmethod
    def from_list(cls, data:list[float]) -> 'Transform':
        if len(data) != 16:
            raise ValueError("transform != 16")
        matrix = np.array(data).reshape(4, 4)
        return cls(matrix)