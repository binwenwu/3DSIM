from __future__ import annotations
import numpy as np
import numpy.typing as npt
from pyproj import CRS


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


if TYPE_CHECKING:
    from typing_extensions import NotRequired


'''
3DTiles type
'''

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


# TODO: Clearly identify the attributes
class PropertyDictType:
    maximum: float
    minimum: float



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







