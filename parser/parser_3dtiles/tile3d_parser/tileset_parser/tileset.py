from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, TYPE_CHECKING

from .type import AssetDictType, GeometricErrorType, TilesetDictType
from .root_property import RootProperty
from .tile import Tile

if TYPE_CHECKING:
    from typing_extensions import Self

#*****************************************
#   Related operations on asset
#*****************************************
class Asset(RootProperty[AssetDictType]):
    def __init__(
        self, version: Literal["1.0", "1.1"] = "1.0", tileset_version: str | None = None, metadataUri: Path | None = None
    ) -> None:
        super().__init__()
        self.version = version
        self.tileset_version = tileset_version
        self.adeOfMetadata = metadataUri

    @classmethod
    # Read asset attribute information from the dictionary
    def from_dict(cls, asset_dict: AssetDictType, metadataPath: Path | None = None) -> Self:
        asset = cls(asset_dict["version"])
        if "tilesetVersion" in asset_dict:
            asset.tileset_version = asset_dict["tilesetVersion"]
        
        if "metadata" in asset_dict:
            asset.adeOfMetadata = metadataPath

        asset.set_properties_from_dict(asset_dict, metadataPath)

        return asset
    
    # Convert asset attribute information into dictionary form
    def to_dict(self) -> AssetDictType:
        asset_dict: AssetDictType = {"version": self.version}

        asset_dict = self.add_root_properties_to_dict(asset_dict, self.adeOfMetadata)

        if self.tileset_version is not None:
            asset_dict["tilesetVersion"] = self.tileset_version

        return asset_dict

#****************************************
#   Related operations on tileset
#****************************************
class TileSet(RootProperty[TilesetDictType]):
    def __init__(
        self,
        geometric_error: float = 500,
        root_uri: Path | None = None,
        metadataUri :Path | None = None
    ) -> None:
        super().__init__()
        self.asset = Asset(version="1.0")
        self.geometric_error: GeometricErrorType = geometric_error
        self.root_tile = Tile()
        self.root_uri = root_uri
        self.extensions_used: str
        self.extensions_required: str
        self.adeOfMetadata = metadataUri

    @classmethod
    # Read tileset related properties from the dictionary
    def from_dict(cls, tileset_dict: TilesetDictType, metadataPath: Path | None = None) -> Self:
        tileset = cls()
        if "geometricError" in tileset_dict:
            tileset.geometric_error = tileset_dict["geometricError"]
        if "metadata" in tileset_dict:
            tileset.adeOfMetadata = metadataPath

        if "asset" in tileset_dict:
            tileset.asset = Asset.from_dict(tileset_dict["asset"], metadataPath)
        
        if "root" in tileset_dict:
            tileset.root_tile = Tile.from_dict(tileset_dict["root"], metadataPath)
        
        tileset.set_properties_from_dict(tileset_dict, metadataPath)

        if "extensionsUsed" in tileset_dict:
            tileset.extensions_used = set(tileset_dict["extensionsUsed"])

        if "extensionsRequired" in tileset_dict:
            tileset.extensions_required = set(tileset_dict["extensionsRequired"])

        return tileset

    @staticmethod
    # 从文件读取json字符串并将其转换为字典，再用from_dict函数将其解析出来
    def from_file(tileset_path: Path) -> TileSet:
        with tileset_path.open() as f:
            tileset_dict = json.load(f)

        tileset = TileSet.from_dict(tileset_dict, tileset_path)

        # 获取tileset.json文件所在目录的路径
        tileset.root_uri = tileset_path.parent

        return tileset
    
    # 删除tileset
    def delete_on_disk(
        self, tileset_path: Path, delete_sub_tileset: bool = False
    ) -> None:
        tileset_path.unlink()
        self.root_tile.delete_on_disk(tileset_path.parent, delete_sub_tileset)


    # 将tileset转化成字典
    def to_dict(self) -> TilesetDictType:
        # self.root_tile.sync_bounding_volume_with_children()

        tileset_dict: TilesetDictType = {}
        if self.asset is not None:
            tileset_dict["asset"] = self.asset.to_dict()
        if self.geometric_error is not None:
            tileset_dict["geometricError"] = self.geometric_error
        if self.root_tile is not None :
            tileset_dict["root"] = self.root_tile.to_dict()

        tileset_dict = self.add_root_properties_to_dict(tileset_dict, self.adeOfMetadata)

        # if self.extensions_used:
        #     tileset_dict["extensionsUsed"] = list(self.extensions_used)
        # if self.extensions_required:
        #     tileset_dict["extensionsRequired"] = list(self.extensions_required)

        return tileset_dict

    # 将字典转化为json字符串
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), indent=2, ensure_ascii=False)
    
    # 将json字符串存储到tileset_path路径下的json文件
    def write_as_json(self, tileset_path: Path) -> None:
        #param tileset_path: the path where the tileset will be written
        with tileset_path.open("w") as f:
            f.write(self.to_json())
