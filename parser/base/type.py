import numpy as np
from enum import Enum

class BoundingVolumeType(Enum):
    AABB = "AABB"
    OBB = "OBB"
    Sphere = "Sphere"

class RangeMode(Enum):
    DISTANCE_FROM_EYE_POINT = "DISTANCE"
    PIXEL_SIZE_ON_SCREEN  = "PIXEL"
    GEOMETRIC_ERROR = "GE"


# class SceneAsset(Enum):
#     CITYGML = "CITYGML"
#     _3DTILES = "_3DTILES"
#     OSG = "OSG"
#     I3S = "I3S"

# class ModelAsset(Enum):
#     POINTCLOUD = "POINTCLOUD"
#     PHYSICALFIELD  = "PHYSICALFIELD"
#     RASTERRELIEF = "RASTERRELIEF"
#     MESH = "3DMESH"

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

class Mesh3DType(Enum):
    PLY = "PLY"
    OBJ = "OBJ"
    FBX = "FBX"




