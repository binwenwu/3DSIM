import numpy as np
from enum import Enum


'''
Unified type
'''

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

class Mesh3DType(Enum):
    GLTF = "GLTF"
    GLB = "PLY"
    FBX = "FBX"

