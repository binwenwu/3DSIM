from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from .type import GeometricErrorType, TilesetDictType
from .root_property import RootProperty
from .tile import Tile
from .asset import Asset

if TYPE_CHECKING:
    from typing_extensions import Self


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
        self.extensions_used: set[str] = set()
        self.extensions_required: set[str] = set()
        self.adeOfMetadata = metadataUri

    @staticmethod
    def from_file(tileset_path: Path) -> TileSet:
        with tileset_path.open() as f:
            tileset_dict = json.load(f)

        tileset = TileSet.from_dict(tileset_dict, tileset_path)
        tileset.root_uri = tileset_path.parent

        return tileset
    
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
        
        # Set the root properties of the tileset
        tileset.set_root_properties_from_dict(tileset_dict, metadataPath)

        # TODO
        # if "extras" in tileset_dict:
        #     tileset.extras = tileset_dict["extras"]

        if "extensionsUsed" in tileset_dict:
            tileset.extensions_used = set(tileset_dict["extensionsUsed"])

        if "extensionsRequired" in tileset_dict:
            tileset.extensions_required = set(tileset_dict["extensionsRequired"])

        return tileset
    

    def to_dict(self) -> TilesetDictType:
        """
        Convert to json string possibly mentioning used schemas
        """
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


    def delete_on_disk(
        self, tileset_path: Path, delete_sub_tileset: bool = False
    ) -> None:
        """
        Deletes all files linked to the tileset. The uri of the tileset should be defined.

        :param tileset_path: The path of the tileset
        :param delete_sub_tileset: If True, all tilesets present as tile content will be removed as well as their content.
        If False, the linked tilesets in tiles won't be removed.
        """
        tileset_path.unlink()
        self.root_tile.delete_on_disk(tileset_path.parent, delete_sub_tileset)
    

    def write_as_json(self, tileset_path: Path) -> None:
        """
        Write the tileset as a JSON file.
        :param tileset_path: the path where the tileset will be written
        """
        with tileset_path.open("w") as f:
            f.write(self.to_json())
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), indent=2, ensure_ascii=False)
