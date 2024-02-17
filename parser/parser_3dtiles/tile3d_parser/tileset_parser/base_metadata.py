from __future__ import annotations

from abc import ABC, abstractmethod

# from tileset.type import MetaDataType
from .type import MetaDataType


class BaseMetadata(ABC):
    """
    A base class to manage 3dtiles metadata.

    If an metadata is added somewhere in a tileset,
    the user must add the name of the extension in the attribute `extensions_used` of the class `TileSet`.
    Also, if the support of an extension is necessary to display the tileset,
    the name must be added in the attribute `extensions_required` of the class `TileSet`.
    """

    def __init__(self, name: str):
        self.name = name

    @classmethod
    @abstractmethod
    def from_dict(cls, metadata_dict: MetaDataType) -> BaseMetadata:
        # @author:wbw
        # 因为这里是抽象类，所以方法体省略
        ...

    @abstractmethod
    def to_dict(self) -> MetaDataType:
        ...
