from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TYPE_CHECKING, TypeVar

from .type import ExtraDictType, MetaDataType, RootPropertyDictType
import json

if TYPE_CHECKING:
    from base_extension import BaseExtension
    from base_metadata import BaseMetadata
    from typing_extensions import Self


# @author:wbw
# 定义泛型类型，并指定其上限为RootPropertyDictType，即该泛型类型变量必须是RootPropertyDictType类型或其子类
_JsonDictT = TypeVar("_JsonDictT", bound = RootPropertyDictType)

#**********************************
#   抽象类，关于一些扩展属性的操作
#**********************************

"""
@author:wbw

这段代码定义了一个名为 `RootProperty` 的 Python 类, 该类是一个抽象类(Abstract Class), 
继承自 `ABC` 类,同时使用了泛型(Generic)类型 `_JsonDictT`。泛型类型 `_JsonDictT` 表示一个字典类型，
用于表示 JSON 数据。在这个类中，使用泛型类型可以使代码更加通用和灵活，可以在子类中指定具体的字典类型。

ABC是一个元类, 用于创建抽象基类。抽象基类不能实例化, 只能被继承。抽象基类的主要作用是强制子类实现特定的方法。
"""
class RootProperty(ABC, Generic[_JsonDictT]):

    def __init__(self,
                 extensions:BaseExtension | None = None) -> None:
        self.metadata: MetaDataType = {}
        self.extensions = extensions
        self.extras: ExtraDictType = {}

    @classmethod
    @abstractmethod
    def from_dict(cls, data_dict: _JsonDictT) -> Self:
        ...

    @abstractmethod
    def to_dict(self) -> _JsonDictT:
        ...

    def add_root_properties_to_dict(
            self,
            dict_data: _JsonDictT,
            filePath: str | None = None) -> _JsonDictT:
        # we cannot merge root_property_data without mypy issues

        if filePath:
            with open(filePath, "r") as f:
                data = json.load(f)
            dict_data["metadata"] = data

        if self.extensions:
            dict_data["extensions"] = self.extensions.to_dict()

        if self.extras:
            dict_data["extras"] = self.extras

        return dict_data

    def set_properties_from_dict(
        self,
        dict_data: _JsonDictT,
        filePath: str | None = None
    ) -> None:
        if "metadata" in dict_data:
            self.metadata = dict_data["metadata"]
            # self.metadata = BaseMetadata.from_dict(dict_data["metadata"])
            # data = json.loads(dict_data["metadata"])
            '''
            如果filePath不为空, 那么就将文件名修改为metadata.json, 并将dict_data["metadata"]写入文件
            '''
            if filePath is not None:
                filePath = filePath.with_name("metadata.json")
                with open(filePath,"a") as f:
                    json.dump(dict_data["metadata"], f)

        if "extensions" in dict_data:
            self.extensions = BaseExtension.from_dict(dict_data["extensions"])

        if "extras" in dict_data:
            self.extras = dict_data["extras"]
