from __future__ import annotations

from .content import Content
from .root_property import RootProperty
from .type import ContentsType

class Contents(RootProperty[ContentsType]):
    def __init__(self) -> None:
        super().__init__()
        self.content: list[Content] = []

    @classmethod
    def from_dict(cls, contents_dict: ContentsType) -> Contents:            
        contents = cls()
        for content in contents_dict:
            content = Content.from_dict(content)
            contents.content.append(content)
        return contents
    
    def to_dict(self) -> ContentsType:
        dict_data: list=[]
        for content in self.content:
            dict_data.append(content.to_dict())
        return dict_data