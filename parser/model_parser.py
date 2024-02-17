import os
from pathlib import Path
from typing import Optional, Tuple


from base.base_3dsim import ThreeDSIMBase
from rmdb_operations.sql_commonds import *

from .parser_physicalfield import ParserPhysicalField
from .parser_pointcloud import ParserPointcloud
from .parser_relief import ParserRelief

class ModelParser(ThreeDSIMBase):
    def __init__(self)-> None:
        super().__init__()
        self._featureType = ''
        self._createTime = ''
        self._validTime = []
        self._modelType = '' 

    # parse a 3d model asset instance file and insert it into 3dsim
    def add_data(self, modelType: str,  path:str, featureType: str='', 
                 createTime: str='', validTime: list[str]=['',''])->None:
        self._featureType = featureType
        self._createTime = createTime
        self._validTime = validTime
        self._modelType = modelType
        self._path = path

        if modelType == 'pointcloud':
            self.add_data_pointcloud()
        elif modelType == 'mesh':
            self.add_data_mesh()
        elif modelType == 'rasterrelief':
            self.add_data_rasterrelief()
        elif modelType == 'physicalField':
            self.add_data_phsicalField()
        else:
            raise ValueError("the model type is not supported currently")

    def add_data_pointcloud(self):
        pc = ParserPointcloud()
        pc.add_data(pointCloudType = "LAZ", path = self._path,createTime=self._createTime, validTime=self._validTime)
        pass
    def add_data_rasterrelief(self):
        pr = ParserRelief()
        pr.add_data(reliefType = 'GEOTIFF', path = self._path,createTime=self._createTime, validTime=self._validTime)
        pass
    def add_data_phsicalField(self):
        pass
    def add_data_mesh(self):
        pass