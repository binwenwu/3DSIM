from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from  base.exceptions import InvalidTilesetError, TilerException
from .type import RefineType, TileDictType
from .bounding_volume import BoundingVolume
from .bounding_volume_box import BoundingVolumeBox
from .bounding_volume_sphere import BoundingVolumeSphere
from .bounding_volume_region import BoundingVolumeRegion
from .content import Content
from .contents import Contents
from .root_property import RootProperty

if TYPE_CHECKING:
    from tileset import TileSet

DEFAULT_TRANSFORMATION = np.identity(4, dtype=np.float64) # Default transformation matrix
DEFAULT_TRANSFORMATION.setflags(write=False) # Set as read-only

#*********************************************************
#   Tile class, defining relevant operations for each tile
#*********************************************************
class Tile(RootProperty[TileDictType]):
    def __init__(
        self,
        geometric_error: float = 500,
        bounding_volume: BoundingVolume[Any] | None = None,
        transform: npt.NDArray[np.float64] = DEFAULT_TRANSFORMATION,
        refine_mode: RefineType = "ADD",
        metadataUri: Path | None = None,
        # content_uri: Path | None = None,
    ) -> None:
        super().__init__()
        self.bounding_volume = bounding_volume
        self.geometric_error = geometric_error
        self._refine: RefineType = "ADD"
        self.set_refine_mode(refine_mode)
        self.content: Content | None = None
        self.contents: Contents | None = None
        self.children: list[Tile] = []
        self.transform = transform
        self.adeOfMetadata = metadataUri
        # self.content_uri: Path | None = content_uri

    @classmethod
    def from_dict(cls, tile_dict: TileDictType, metadataPath: Path | None = None) -> Tile:
        tile = cls()
        if "box" in tile_dict["boundingVolume"]:
            tile.bounding_volume = BoundingVolumeBox.from_dict(tile_dict["boundingVolume"])
        elif "region" in tile_dict["boundingVolume"]:
            tile.bounding_volume = BoundingVolumeRegion.from_dict(tile_dict["boundingVolume"])
        elif "sphere" in tile_dict["boundingVolume"]:
            tile.bounding_volume = BoundingVolumeSphere.from_dict(tile_dict["boundingVolume"])
        else:
            raise InvalidTilesetError(
                f"The bounding volume {list(tile_dict['boundingVolume'].keys())[0]} is unknown"
            )
        if "geometricError" in tile_dict:
            tile.geometric_error = tile_dict["geometricError"]

        if "metadata" in tile_dict:
            tile.adeOfMetadata = metadataPath

        if "refine" in tile_dict:
            tile.set_refine_mode(tile_dict["refine"])

        if "transform" in tile_dict:
            tile.transform = np.array(tile_dict["transform"]).reshape((4, 4))

        if "children" in tile_dict:
            for child in tile_dict["children"]:
                tile.children.append(Tile.from_dict(child))

        if "content" in tile_dict:
            tile.content = Content.from_dict(tile_dict["content"])
            # tile.content_uri = Path(tile_dict["content"]["uri"])
        elif "contents" in tile_dict:
            tile.contents = Contents.from_dict(tile_dict["contents"])

        tile.set_properties_from_dict(tile_dict, metadataPath)

        return tile

    def has_content(self) -> bool:
        """
        Returns if there is a tile content (loaded or not).
        """
        return bool(self.content is not None)
    
    def has_contents(self) -> bool:
        return bool(self.contents is not None)


    def delete_on_disk(self, root_uri: Path, delete_sub_tileset: bool = False) -> None:
        """
        Deletes all files linked to the tile and its children. The uri of the folder where tileset is, should be defined.

        :param root_uri: The folder where tileset is
        :param delete_sub_tileset: If True, all tilesets present as tile content will be removed as well as their content.
        If False, the linked tilesets in tiles won't be removed.
        """
        for child in self.children:
            child.delete_on_disk(root_uri, delete_sub_tileset)

        # if there is no content_uri, there is no file to remove
        if self.content is None:
            return
        
        if self.content.content_uri.is_absolute():
            tile_content_path = self.content.content_uri
        else:
            tile_content_path = root_uri / self.content.content_uri

        if tile_content_path.suffix == ".json":
            if delete_sub_tileset:
                self.get_or_fetch_content(root_uri).delete_on_disk(tile_content_path)  # type: ignore
        else:
            tile_content_path.unlink()

    
    def set_refine_mode(self, mode: RefineType) -> None:
        if mode != "ADD" and mode != "REPLACE" and mode!=None:
            raise InvalidTilesetError(
                f"Unknown refinement mode {mode}. Should be either 'ADD' or 'REPLACE'."
            )
        self._refine = mode
    

    def get_refine_mode(self) -> RefineType:
        return self._refine
    

    def add_child(self, tile: Tile) -> None:
        self.children.append(tile)

        if tile.bounding_volume is not None:
            if self.bounding_volume is None:
                self.bounding_volume = copy.deepcopy(tile.bounding_volume)


    def get_children(self) -> list[Tile]:
        children = []
        for child in self.children:
            children.append(child)
        return children


    def get_all_children(self) -> list[Tile]:
        """
        :return: the recursive (across the children tree) list of the children tiles
        """
        descendants = []
        for child in self.children:
            # Add the child...
            descendants.append(child)
            # and if (and only if) they are grand-children then recurse
            if child.children:
                descendants += child.get_all_children()
        return descendants


    def to_dict(self) -> TileDictType:
        dict_data: TileDictType = {}
        if self.bounding_volume is not None:
            bounding_volume = self.bounding_volume
            if bounding_volume is not None:
                dict_data["boundingVolume"] = bounding_volume
        else:
            raise InvalidTilesetError("Bounding volume is not set")
        
        if self._refine is not None:
            if self._refine not in ["ADD", "REPLACE"]:
                raise InvalidTilesetError(
                    f"refine should be either ADD or REPLACE, currently {self._refine}."
                )
            dict_data["refine"] = self._refine

        if self.geometric_error is not None:
            dict_data["geometricError"] = self.geometric_error


        dict_data = self.add_root_properties_to_dict(dict_data, self.adeOfMetadata)

        if (
            self.transform is not None and self.transform is not DEFAULT_TRANSFORMATION
        ):
            self.transform = self.strToTransformMatrix(self.transform)
            if self.transform.size != 0:
                dict_data["transform"] = list(self.transform.flatten())

        if self.children:
            dict_data["children"] = [child.to_dict() for child in self.children]

        if self.content:
            dict_data["content"] = self.content.to_dict()
        elif self.contents:
            dict_data["contents"] = self.contents.to_dict()
            
        return dict_data
    

    def strToBoundingVolumeType(self, boundingVolume_dict: dict):
        if boundingVolume_dict is not None:
            str_list = [value for value in boundingVolume_dict.values()]
            if str_list[0] is not None:
                # 删除大括号
                str_list = str_list[0].strip('{}')
                # 使用逗号分隔字符串，并将数字字符串转换为浮点数
                float_list = [float(x) for x in str_list.split(',')]

                boundingVolumeDictKeys = [value for value in boundingVolume_dict.keys()][0]
                boundingVolume_dict[boundingVolumeDictKeys] = float_list
                if "box" in boundingVolume_dict:
                    bounding_volume = BoundingVolumeBox.from_dict(boundingVolume_dict)
                elif "region" in boundingVolume_dict:
                    bounding_volume=BoundingVolumeRegion.from_dict(boundingVolume_dict)
                elif "sphere" in boundingVolume_dict:
                    bounding_volume = BoundingVolumeSphere.from_dict(boundingVolume_dict)
                else:
                    raise InvalidTilesetError(
                        f"The bounding volume {list(boundingVolume_dict.keys())[0]} is unknown"
                    )
                return bounding_volume

    def strToTransformMatrix(self,strTransformMatrix):
        if strTransformMatrix != 'None':
            strTransformMatrix.replace('{', '').replace('}', '').replace(',', '')
            arr = np.fromstring(strTransformMatrix, sep=' ')
            return arr




