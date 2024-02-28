from __future__ import annotations

import numpy as np
import numpy.typing as npt

from .root_property import RootProperty
from .type import ContentType
from  base.exceptions import InvalidTilesetError
from .bounding_volume import BoundingVolume
from .bounding_volume_box import BoundingVolumeBox
from .bounding_volume_sphere import BoundingVolumeSphere
from .bounding_volume_region import BoundingVolumeRegion
from typing import Any
from pathlib import Path

DEFAULT_TRANSFORMATION = np.identity(4, dtype=np.float64)
DEFAULT_TRANSFORMATION.setflags(write=False)

class Content(RootProperty[ContentType]):
    def __init__(self,
                 bounding_volume: BoundingVolume[Any] | None = None,
                 transform: npt.NDArray[np.float64] | None = None,
                 content_uri: Path | None = None,
                 metadataPath: Path | None = None
                 ) -> None:
        super().__init__()
        self.bounding_volume = bounding_volume
        self.transform = transform
        self.content_uri: Path | None = content_uri
        self.adeOfMetadata: Path | None = metadataPath

    @classmethod
    def from_dict(cls, content_dict: ContentType, metadataPath: Path | None = None) -> Content:
        content = cls()
        if "boundingVolume" in content_dict:
            if "box" in content_dict["boundingVolume"]:
                bounding_volume = BoundingVolumeBox.from_dict(content_dict["boundingVolume"])
            elif "region" in content_dict["boundingVolume"]:
                bounding_volume=BoundingVolumeRegion.from_dict(content_dict["boundingVolume"])
            elif "sphere" in content_dict["boundingVolume"]:
                bounding_volume = BoundingVolumeSphere.from_dict(content_dict["boundingVolume"])
            else:
                raise InvalidTilesetError(
                    f"The bounding volume {list(content_dict['boundingVolume'].keys())[0]} is unknown"
                )
            content.bounding_volume = bounding_volume
            
        if "uri" in content_dict:
            content.content_uri = Path(content_dict["uri"])
            # content.content_uri = Path(content_dict["uri"]).absolute()
        
        if "metadata" in content_dict:
            content.adeOfMetadata = metadataPath

        if "transform" in content_dict:
            content.transform = np.array(content_dict["transform"]).reshape((4, 4))

        content.set_properties_from_dict(content_dict, metadataPath)

        return content
    
    def to_dict(self) -> ContentType:
        dict_data: Content = {}
        if self.bounding_volume is not None:
            bounding_volume = self.bounding_volume
            if bounding_volume is not None:
                dict_data["boundingVolume"] = bounding_volume

        if (
            self.transform is not None and self.transform is not DEFAULT_TRANSFORMATION
        ):
            self.transform = self.strToTransformMatrix(self.transform)
            if self.transform.size != 0:
                dict_data["transform"] = list(self.transform.flatten())

        if self.content_uri is not None:
            dict_data["uri"] = self.content_uri
        
        dict_data = self.add_root_properties_to_dict(dict_data, self.adeOfMetadata)

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