from __future__ import annotations
import numpy as np
import numpy.typing as npt
from pyproj import CRS

"""
TYPE_CHECKING：用于在类型注解中检查类型的特殊常量。
Any：表示任意类型。
Dict：表示字典类型，接受两个类型参数，分别表示键和值的类型。
List：表示列表类型，接受一个类型参数，表示列表元素的类型。
Literal：表示字面值类型，接受一个或多个字面值作为参数。
Optional：表示可选类型，可以为指定类型或 None。
Tuple：表示元组类型，接受一个或多个类型参数，表示元组中每个位置的类型。
TypedDict：表示有类型的字典类型，用于定义带有特定字段和类型的字典。
Union：表示联合类型，接受两个或多个类型参数，表示可以是其中任意一个类型
"""
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    TypedDict,
    Union,
)


# @author:wbw
# NotRequired 类型是一个自定义类型，它表示一个可选的值，可以是任何类型或 None。它通常用于类型注解中, 表示一个参数或返回值是可选的。

if TYPE_CHECKING:
    from typing_extensions import NotRequired

# Tileset types
MetaDataType = Dict[str, Any]
ExtensionDictType = Dict[str, Any]
ExtraDictType = Dict[str, Any]
GeometricErrorType = float
PropertyType = Dict[str, Any]
RefineType = Literal["ADD", "REPLACE"]
TransformDictType = List[float]



class RootPropertyDictType(TypedDict):
    metadata: NotRequired[MetaDataType]
    extensions: NotRequired[ExtensionDictType]
    extras: NotRequired[ExtraDictType]



class BoundingVolumeBoxDictType(RootPropertyDictType):
    box: list[float]


class BoundingVolumeRegionDictType(RootPropertyDictType):
    region: list[float]

class BoundingVolumeSphereDictType(RootPropertyDictType):
    sphere: list[float]


BoundingVolumeDictType = Union[
    BoundingVolumeBoxDictType,
    BoundingVolumeRegionDictType,
    BoundingVolumeSphereDictType,
]


class ContentType(RootPropertyDictType):
    boundingVolume: NotRequired[BoundingVolumeDictType]
    transform: NotRequired[TransformDictType]
    uri: str




class ContentsType(RootPropertyDictType):
    content: list[ContentType]



class PropertyDictType:
    # TODO 这个还没同步到输出的tileset.json中
    Height: PropertyType
    Latitude: PropertyType
    Longitude: PropertyType



class AssetDictType(RootPropertyDictType):
    version: Literal["1.0", "1.1"]
    tilesetVersion: NotRequired[str]



class TileDictType(RootPropertyDictType):
    boundingVolume: BoundingVolumeDictType
    geometricError: GeometricErrorType
    viewerRequestVolume: NotRequired[BoundingVolumeDictType]
    refine: NotRequired[RefineType]
    transform: NotRequired[TransformDictType]
    content: NotRequired[ContentType]
    children: NotRequired[list[TileDictType]]


class TilesetDictType(RootPropertyDictType):
    asset: AssetDictType
    geometricError: GeometricErrorType
    root: TileDictType
    properties: PropertyDictType
    extensionsUsed: NotRequired[list[str]]
    extensionsRequired: NotRequired[list[str]]



# TODO 以下参考py3dtiles
# BatchTableDictType = Dict[str, Any]

# # Tile content types

# BatchTableHeaderDataType = Dict[str, Union[List[Any], Dict[str, Any]]]

# FeatureTableHeaderDataType = Dict[
#     str,
#     Union[
#         int,  # points_length
#         Dict[str, int],  # byte offsets
#         Tuple[float, float, float],  # rtc
#         List[float],  # quantized_volume_offset and quantized_volume_scale
#         Tuple[int, int, int, int],  # constant_rgba
#     ],
# ]


# class HierarchyClassDictType(TypedDict):
#     name: str
#     length: int
#     instances: dict[str, list[Any]]


# # Tiler types

# PortionItemType = Tuple[int, ...]
# PortionsType = List[Tuple[str, PortionItemType]]


# class MetadataReaderType(TypedDict):
#     portions: PortionsType
#     aabb: npt.NDArray[np.float64]
#     crs_in: CRS | None
#     point_count: int
#     avg_min: npt.NDArray[np.float64]


# OffsetScaleType = Tuple[
#     npt.NDArray[np.float64],
#     npt.NDArray[np.float64],
#     Optional[npt.NDArray[np.float64]],
#     Optional[float],
# ]




