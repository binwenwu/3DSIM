"""
@author:wbw
@description: 该模块定义了在 tileset_parser 模块中解析三维瓦片集合的数据类型.

- `ExtraDictType`：包含拓展属性的字典。
- `MetaDataType`：包含有关瓦片集的元数据的字典。
- `GeometricErrorType`：表示瓦片的几何误差的浮点数。
- `PropertyType`：包含瓦片属性的字典。
- `RefineType`：表示应用于瓦片的细化类型的字符串字面量。
- `TransformDictType`：表示 4x4 矩阵变换的 16 个浮点数列表。

- `RootPropertyDictType`：包含瓦片集根级别属性的字典。
- `BoundingVolumeBoxDictType`：包含瓦片集边界框的字典。
- `BoundingVolumeRegionDictType`：包含瓦片集边界区域的字典。
- `BoundingVolumeSphereDictType`：包含瓦片集边界球的字典。
- `BoundingVolumeDictType`：三种边界体类型的基类。
- `ContentType`：包含瓦片内容属性的字典。
- `ContentsType`：包含瓦片内容列表的字典。
- `PropertyDictType`：包含瓦片属性的字典。
- `AssetDictType`：包含瓦片集资产属性的字典。
- `TileDictType`：包含瓦片属性的字典。
- `TilesetDictType`：包含瓦片集属性的字典。
"""
from __future__ import annotations


"""
@author:wbw
- `Any`：表示任意类型。
- `Dict`：表示字典类型，其中键为字符串，值为任意类型。
- `List`：表示列表类型，其中元素为任意类型。
- `Literal`：表示字面量类型，用于指定一个固定的值。
- `TYPE_CHECKING`：一个常量，用于在类型注解中进行条件导入。
- `TypedDict`：表示字典类型，其中键和值都有指定的类型。
- `Union`：表示联合类型，其中至少有一个类型匹配。
"""
from typing import (
    Any,
    Dict,
    List,
    Literal,
    TYPE_CHECKING,
    TypedDict,
    Union,
)


# @author:wbw
# NotRequired 类型是一个自定义类型，它表示一个可选的值，可以是任何类型或 None。它通常用于类型注解中, 表示一个参数或返回值是可选的。

if TYPE_CHECKING:
    from typing_extensions import NotRequired

# Tileset types
ExtensionDictType = Dict[str, Any]
ExtraDictType = Dict[str, Any]
MetaDataType = Dict[str, Any]
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



# @author:wbw
# 表示一个瓦片集的边界体的字典类型，可以是一个边界框、边界区域或边界球中的任意一种
BoundingVolumeDictType = Union[
    BoundingVolumeBoxDictType,
    BoundingVolumeRegionDictType,
    BoundingVolumeSphereDictType,
]


# @author:wbw
class ContentType(RootPropertyDictType):
    boundingVolume: NotRequired[BoundingVolumeDictType]
    transform: NotRequired[TransformDictType]
    uri: str



# @author:wbw
class ContentsType(RootPropertyDictType):
    content: list[ContentType]


# @author:wbw
# 这个类的作用是什么？
class PropertyDictType:
    maximum: float
    minimum: float


# @author:wbw
# 表示瓦片集的资产属性
class AssetDictType(RootPropertyDictType):
    version: Literal["1.0", "1.1"]
    tilesetVersion: NotRequired[str]


# @author:wbw
# 表示一个瓦片的属性
class TileDictType(RootPropertyDictType):
    boundingVolume: BoundingVolumeDictType
    geometricError: GeometricErrorType
    viewerRequestVolume: NotRequired[BoundingVolumeDictType]
    refine: NotRequired[RefineType]
    transform: NotRequired[TransformDictType]
    content: NotRequired[ContentType]
    children: NotRequired[list[TileDictType]]


# @author:wbw
# 表示一个瓦片集的属性
# root 是干嘛的？
class TilesetDictType(RootPropertyDictType):
    asset: AssetDictType
    properties: PropertyDictType
    geometricError: GeometricErrorType
    root: TileDictType
    extensionsUsed: NotRequired[list[str]]
    extensionsRequired: NotRequired[list[str]]

