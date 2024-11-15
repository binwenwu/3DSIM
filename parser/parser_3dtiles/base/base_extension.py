from __future__ import annotations

from abc import ABC, abstractmethod
from .type import ExtensionDictType



class BaseExtension():
    """
    A base class to manage 3dtiles extension.

    If an extension is added somewhere in a tileset,
    the user must add the name of the extension in the attribute `extensions_used` of the class `TileSet`.
    Also, if the support of an extension is necessary to display the tileset,
    the name must be added in the attribute `extensions_required` of the class `TileSet`.
    """

    def __init__(self, name: str | None = None,
                 identifier: str | None = None,
                 creatDate: str | None = None,
                 validFrom: str | None = None,
                 validTo: str | None = None):
        self.name = name
        self.identifier = identifier
        self.createDate = creatDate
        self.validFrom = validFrom
        self.validTo = validTo

   
    @classmethod
    def from_dict(cls, extension_dict: ExtensionDictType) -> BaseExtension:

        if "name" in extension_dict:
            name = extension_dict["name"]
        
        # Create a new extension object from the dictionary
        extensions = cls(name=name)
        if "identifier" in extension_dict:
            extensions.identifier = extension_dict["identifier"]
        
        if "creatDate" in extension_dict:
            extensions.createDate = extension_dict["createDate"]

        if "validFrom" in extension_dict:
            extensions.validFrom = extension_dict["validFrom"]
        
        if "validTo" in extension_dict:
            extensions.validTo = extension_dict["validTo"]

        return extensions


    # Convert extended objects to dictionaries
    def to_dict(self) -> ExtensionDictType:
        dict_data: ExtensionDictType = {}
        if self.name:
            dict_data["name"] = self.name

        if self.identifier:
            dict_data["identifier"] = self.identifier

        if self.createDate:
            dict_data["createDate"] = self.createDate

        if self.validFrom:
            dict_data["validFrom"] = self.validFrom

        if self.validTo:
            dict_data["validTo"] = self.validTo

        return dict_data

