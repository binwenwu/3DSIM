from __future__ import annotations

from pathlib import Path
from typing import Literal, TYPE_CHECKING

from .type import AssetDictType
from .root_property import RootProperty

if TYPE_CHECKING:
    from typing_extensions import Self



#*****************************************
#   Related operations on asset
#*****************************************
class Asset(RootProperty[AssetDictType]):
    def __init__(
        self, version: Literal["1.0", "1.1"] = "1.0", tileset_version: str | None = None, metadataPath: Path | None = None
    ) -> None:
        super().__init__()
        self.version = version
        self.tileset_version = tileset_version
        self.adeOfMetadata = metadataPath

    @classmethod
    # Read asset attribute information from the dictionary
    def from_dict(cls, asset_dict: AssetDictType, metadataPath: Path | None = None) -> Self:
        asset = cls(asset_dict["version"])
        if "tilesetVersion" in asset_dict:
            asset.tileset_version = asset_dict["tilesetVersion"]
        if "metadata" in asset_dict:
            asset.adeOfMetadata = metadataPath

        asset.set_root_properties_from_dict(asset_dict, metadataPath)

        return asset
    
    # Convert asset attribute information into dictionary form
    def to_dict(self) -> AssetDictType:
        asset_dict: AssetDictType = {"version": self.version}

        asset_dict = self.add_root_properties_to_dict(asset_dict, self.adeOfMetadata)

        if self.tileset_version is not None:
            asset_dict["tilesetVersion"] = self.tileset_version

        return asset_dict