import os
from pathlib import Path
from typing import Optional, Tuple

from parser.base.bounding_volume import BoundingVolume, InputBVType
from parser.base.Transform import Transform
from tools.render_range_convert import RangeMode, RangeConverter
from bson import ObjectId
from base.base_3dsim import ThreeDSIMBase
from rmdb_operations.sql_commonds import *
from mongodb_operations.mongo_template import template_scene_asset, template_asset_edge, template_model_asset
from mongodb_operations.mongodb import MongoDB
from data_operations.query import Query
from data_operations.remove import Remove

from .base.tileset import TileSet
from .base.asset import Asset
from .base.tile import Tile
from .base.content import Content
from .base.contents import Contents



from tools.utils import generate_short_hash
from minio_operations.minio import get_endpoint_minio
from typing import Union
class Parser3DTiles(ThreeDSIMBase):
    def __init__(self)-> None:
        super().__init__()
        self._featureType = ''
        self._createTime = ''
        self._validTime = []
        self._tileset = None
        self._tileset_dict = None

        # for counting the node number of a 3d tiles
        self._counter_subscenes = 0 
        self._counter_submodels = 0

    '''
    parse a3dtile instance file and insert it into 3dsim
    '''
    def add_data(self, path:str, featureType: str='', 
                 createTime: str='', validTime: list[str]=['',''])->None:
        self._featureType = featureType
        self._createTime = createTime
        self._validTime = validTime
        self._tileset_dict, self._tileset = TileSet.from_file(Path(path))
        print("## the 3d tile inserting ...")
        self._convert_tile_to_fact(self._tileset.root_tile, isRoot=True)
        print("## the 3d tile inserted")


    def _convert_tile_to_fact(self, tile:Tile, isRoot: bool=False, fatherID: dict={}) -> dict:
        pass
    
