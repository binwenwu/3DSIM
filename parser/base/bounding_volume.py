from enum import Enum
import numpy as np
from pyproj import Transformer, CRS
from typing import List, Tuple, Union
from math import pi

from .type import BoundingVolumeType

class InputBVType(Enum):
    Box_3dtile = "Box_3dtile"
    Region_3dtile = "Region_3dtile"
    Sphere_3dtile = "Sphere_3dtile"

class BoundingVolume:
    def __init__(self):
        pass
    
    # Convert the bounding box type in 3dtiles to a standard bounding box type
    @staticmethod
    def convert_3dtilesBV_to_standardBV(input_bv_type: InputBVType, bv_data: list) -> dict:
        if input_bv_type == InputBVType.Box_3dtile:
            return BoundingVolume._convert_box_to_obb(bv_data)
        elif input_bv_type == InputBVType.Region_3dtile:
            return BoundingVolume._convert_region_to_aabb(bv_data)
        elif input_bv_type == InputBVType.Sphere_3dtile:
            return BoundingVolume._convert_sphere_to_sphere(bv_data)        
        else:
            raise ValueError("Unsupported Bounding Volume Type.")
        
    
    @staticmethod
    def convert_standardBV_to_3dtilesBV(boundingVolume: dict) -> dict:
        bvType = boundingVolume['type']
        bv = boundingVolume['bv']
        if bvType == BoundingVolumeType.AABB.value:
            return {
                    "region": BoundingVolume._aabb_to_3dtiles_region(bv)
            }
        elif bvType == BoundingVolumeType.OBB.value:
            return {
                    "box": BoundingVolume._obb_to_3dtiles_box(bv)
            }
        elif bvType == BoundingVolumeType.Sphere.value:
            return {
                    "sphere": BoundingVolume._sphere_to_3dtiles_sphere(bv)
            }
        else:
            print(boundingVolume)
            raise ValueError("Unsupported Bounding Volume Type.")
    

    @staticmethod
    def convert_to_standardAABB(west: float, south: float, 
                               east: float, north: float,
                               min_height: float, max_height: float) -> dict:
        aabb_data = [west, south, min_height, east, north, max_height]
        bv = {
            "boundingVolume":{
                    "type": "AABB",
                    "bv": aabb_data
                }
        }
        return bv
    

    @staticmethod
    def convert_standardBV_to_standardAABB(input: dict) -> dict:
        bv = input["boundingVolume"]
        if bv["type"] == BoundingVolumeType.AABB.value:
            return bv
        elif bv["type"] == BoundingVolumeType.OBB.value:
            obb_data = bv["bv"]
            center = obb_data[:3]
            size = obb_data[3:6]
            # Calculate the AABB data [min_x, min_y, min_z, max_x, max_y, max_z]
            aabb_data = [
                center[0] - size[0] / 2,  # min_x
                center[1] - size[1] / 2,  # min_y
                center[2] - size[2] / 2,  # min_z
                center[0] + size[0] / 2,  # max_x
                center[1] + size[1] / 2,  # max_y
                center[2] + size[2] / 2   # max_z
            ]
            return {
                "boundingVolume":{
                    "type": "AABB",
                    "bv": aabb_data
                }
            }
        elif bv["type"] == BoundingVolumeType.Sphere.value:
            sphere_data = bv["bv"]
            center = sphere_data["center"]
            radius = sphere_data["radius"]
            # Calculate the AABB data [min_x, min_y, min_z, max_x, max_y, max_z]
            aabb_data = [
                center[0] - radius,  # min_x
                center[1] - radius,  # min_y
                center[2] - radius,  # min_z
                center[0] + radius,  # max_x
                center[1] + radius,  # max_y
                center[2] + radius   # max_z
            ]
            return {
                "boundingVolume":{
                    "type": "AABB",
                    "bv": aabb_data
                }
            }
        else:
            raise ValueError("Unsupported Bounding Volume Type.")
    
    @staticmethod
    def _convert_box_to_obb(box_list: List[float]) -> dict:
        box = np.array(box_list, dtype=float)
        if len(box) != 12:
            raise ValueError("Warning: Bounding Volume Box must have 12 elements.")

        # Extract the box parameters
        center = box[:3]  # Center point coordinates (x, y, z)

        # Extract the direction vectors and half-lengths
        x_dir = box[3:6]  # x-axis direction vector and half-length
        y_dir = box[6:9]  # y-axis direction vector and half-length
        z_dir = box[9:12]  # z-axis direction vector and half-length

        # Calculate the size (width, height, depth)
        size = np.linalg.norm(np.array([x_dir, y_dir, z_dir]), axis=1) * 2

        # Construct the rotation matrix
        rotation_matrix = np.array([x_dir, y_dir, z_dir]).T

        # Construct the OBB data [center_x, center_y, center_z, size_x, size_y, size_z, r00, r01, r02, r10, r11, r12, r20, r21, r22]
        obb_data = [*center, *size, *rotation_matrix.flatten()]

        bv = {
            "boundingVolume":{
                    "type": "OBB",
                    "bv": obb_data
                }
        }
        return bv

    @staticmethod
    def _convert_region_to_aabb(region_list: List[float]) -> dict:
        # refer to 3D Tiles specification BoundingVolume.region

        region = BoundingVolume._arc_to_wgs84(region_list)# Convert the region parameters from radians to degrees

        west, south, east, north, min_height, max_height = region

        # Construct the AABB data [min_x, min_y, min_z, max_x, max_y, max_z]
        aabb_data = [west, south, min_height,
                     east, north, max_height]

        bv = {
            "boundingVolume":{
                    "type": "AABB",
                    "bv": aabb_data
                }
        }
        return bv
    
    @staticmethod
    def _convert_sphere_to_sphere(sphere_list: List[float]) -> dict:
        center_x, center_y, center_z, radius = sphere_list
        sphere_data = {
            "center": [center_x, center_y, center_z],
            "radius": radius
        }

        bv = {
            "boundingVolume":{
                    "type": "Sphere",
                    "bv": sphere_data
            }
        }
        return bv

    # radians coods to lan/lat coords
    @staticmethod
    def _arc_to_wgs84(region_list: List[float]) -> List[float]:
        west, south, east, north, min_height, max_height = region_list
        west = 180/pi * west
        south = 180/pi *south
        east = 180/pi *east
        north = 180/pi *north
        return [west, south, east, north, min_height, max_height]

    @staticmethod
    def _aabb_to_3dtiles_region(aabb_data: List[float]) -> List[float]:
        # Calculate the region parameters from AABB data in degrees
        west, south, min_height, east, north, max_height = aabb_data
        west = pi / 180 * west
        south = pi / 180 * south
        east = pi / 180 * east
        north = pi / 180 * north
        return [west, south, east, north, min_height, max_height]

    @staticmethod
    def _obb_to_3dtiles_box(obb_data: List[float]) -> List[float]:
        # Convert the OBB data to Box data (center_x, center_y, center_z, size_x, size_y, size_z)
        center_x, center_y, center_z, size_x, size_y, size_z, r00, r01, r02, r10, r11, r12, r20, r21, r22 = obb_data
        size_x *= 2
        size_y *= 2
        size_z *= 2
        return [center_x, center_y, center_z, size_x, size_y, size_z]

    @staticmethod
    def _sphere_to_3dtiles_sphere(sphere_data: dict) -> List[float]:
        center_x, center_y, center_z = sphere_data["center"]
        radius = sphere_data["radius"]
        return [center_x, center_y, center_z, radius]