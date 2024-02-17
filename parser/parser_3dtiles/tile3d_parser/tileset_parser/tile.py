from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from .exceptions import InvalidTilesetError, TilerException
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

DEFAULT_TRANSFORMATION = np.identity(4, dtype=np.float64) # 生成一个4*4的单位矩阵,默认的变换矩阵
DEFAULT_TRANSFORMATION.setflags(write=False) # 设置为只读

#**************************************
#   Tile类，定义关于每个tile的相关操作
#**************************************
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

    @classmethod
    # 从字典中获取tile
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

    # 删除tile
    def delete_on_disk(self, root_uri: Path, delete_sub_tileset: bool = False) -> None:
        for child in self.children:
            child.delete_on_disk(root_uri, delete_sub_tileset)

        if self.content is None:
            return

        # @author:wbw
        # 然后，判断当前节点是否包含内容对象。如果不包含，则直接返回。
        # 否则，判断内容对象的 URI 是否为绝对路径。如果是，则将其赋值给 tile_content_path 变量；
        # 否则，将 root_uri 和内容对象的 URI 拼接起来，赋值给 tile_content_path 变量。
        # 最后，使用 unlink 方法删除 tile_content_path 变量所表示的文件。
        if self.content.content_uri.is_absolute():
            tile_content_path = self.content.content_uri
        else:
            tile_content_path = root_uri / self.content.content_uri

        tile_content_path.unlink()
    
    # 设置refine的模式：ADD or REPLACE
    def set_refine_mode(self, mode: RefineType) -> None:
        if mode != "ADD" and mode != "REPLACE" and mode!=None:
            raise InvalidTilesetError(
                f"Unknown refinement mode {mode}. Should be either 'ADD' or 'REPLACE'."
            )
        self._refine = mode
    
    # 获得remode模式
    def get_refine_mode(self) -> RefineType:
        return self._refine
    
    # 给tile增加孩子结点
    def add_child(self, tile: Tile) -> None:
        self.children.append(tile)

        if tile.bounding_volume is not None:
            if self.bounding_volume is None:
                self.bounding_volume = copy.deepcopy(tile.bounding_volume)

    # 获取某个结点的孩子结点
    def get_children(self) -> list[Tile]:
        children = []
        for child in self.children:
            children.append(child)
        return children

    # 获取所有子孙节点
    def get_all_children(self) -> list[Tile]:
        descendants = []
        for child in self.children:
            descendants.append(child)
            if child.children:
                descendants += child.get_all_children()
        return descendants


    # 将tile转化为字典
    def to_dict(self) -> TileDictType:
        dict_data: TileDictType = {}
        if self.bounding_volume is not None:
            # print(self.bounding_volume)
            bounding_volume = self.bounding_volume
            if bounding_volume is not None:
                dict_data["boundingVolume"] = bounding_volume
        
        if self._refine is not None:
            if self._refine not in ["ADD", "REPLACE"]:
                raise InvalidTilesetError(
                    f"refine should be either ADD or REPLACE, currently {self._refine}."
                )
            dict_data["refine"] = self._refine

        if self.geometric_error is not None:
            dict_data["geometricError"] = self.geometric_error

        # @author:wbw
        # 为什么是以这种方式去加 (原始基类就有的就直接加，继承后才有的属性通过该方法加？)
        dict_data = self.add_root_properties_to_dict(dict_data, self.adeOfMetadata)

        if (
            self.transform is not None and self.transform is not DEFAULT_TRANSFORMATION
        ):
            self.transform = self.strToTransformMatrix(self.transform)
            if self.transform.size != 0:
                dict_data["transform"] = list(self.transform.flatten())

        if self.children:
            # print(self.children)
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
        # 去掉大括号和逗号
        if strTransformMatrix != 'None':
            strTransformMatrix.replace('{', '').replace('}', '').replace(',', '')
            # 使用 fromstring() 函数将字符串转换为一维数组
            arr = np.fromstring(strTransformMatrix, sep=' ')

            return arr




