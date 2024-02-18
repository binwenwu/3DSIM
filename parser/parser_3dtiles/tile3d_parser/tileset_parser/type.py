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


# 描述3DTiles内容的基类
class RootPropertyDictType(TypedDict):
    metadata: NotRequired[MetaDataType]
    extensions: NotRequired[ExtensionDictType]
    extras: NotRequired[ExtraDictType]


# tileset.json的字典类型
class TilesetDictType(RootPropertyDictType):
    asset: AssetDictType
    properties: PropertyDictType
    geometricError: GeometricErrorType
    root: TileDictType
    extensionsUsed: NotRequired[list[str]]
    extensionsRequired: NotRequired[list[str]]



class BoundingVolumeBoxDictType(RootPropertyDictType):
    box: list[float]


class BoundingVolumeRegionDictType(RootPropertyDictType):
    region: list[float]

class BoundingVolumeSphereDictType(RootPropertyDictType):
    sphere: list[float]

# tileset.json中boundingVolume属性的字典类型
BoundingVolumeDictType = Union[
    BoundingVolumeBoxDictType,
    BoundingVolumeRegionDictType,
    BoundingVolumeSphereDictType,
]


# tileset.json中content属性的字典类型
class ContentType(RootPropertyDictType):
    boundingVolume: NotRequired[BoundingVolumeDictType]
    transform: NotRequired[TransformDictType]
    uri: str



# tileset.json中contents属性的字典类型
class ContentsType(RootPropertyDictType):
    content: list[ContentType]


# tileset.json中properties根属性的字典类型
class PropertyDictType:
    # TODO 这个还没同步到输出的tileset.json中
    Height: PropertyType
    Latitude: PropertyType
    Longitude: PropertyType


# tileset.json中asset根属性的字典类型
class AssetDictType(RootPropertyDictType):
    version: Literal["1.0", "1.1"]
    tilesetVersion: NotRequired[str]


# tileset.json中一个tile的字典类型
class TileDictType(RootPropertyDictType):
    boundingVolume: BoundingVolumeDictType
    geometricError: GeometricErrorType
    viewerRequestVolume: NotRequired[BoundingVolumeDictType]
    refine: NotRequired[RefineType]
    transform: NotRequired[TransformDictType]
    content: NotRequired[ContentType]
    children: NotRequired[list[TileDictType]]





