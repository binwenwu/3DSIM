from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TYPE_CHECKING, TypeVar

from .type import ExtraDictType, MetaDataType, RootPropertyDictType
import json

if TYPE_CHECKING:
    from base_extension import BaseExtension
    from base_metadata import BaseMetadata
    from typing_extensions import Self



_JsonDictT = TypeVar("_JsonDictT", bound = RootPropertyDictType)

#*****************************************
#   operations on some extended properties
#*****************************************

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
            # If filePath is not empty, then change the file name to metadata.json and write dict_data ["metadata"] to the file
            if filePath is not None:
                filePath = filePath.with_name("metadata.json")
                with open(filePath,"a") as f:
                    json.dump(dict_data["metadata"], f)

        if "extensions" in dict_data:
            self.extensions = BaseExtension.from_dict(dict_data["extensions"])

        if "extras" in dict_data:
            self.extras = dict_data["extras"]
