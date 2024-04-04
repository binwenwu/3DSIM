import os
from pathlib import Path
from typing import Optional, Tuple
import json
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
from data_operations.update import Update

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
        _tileset_dict, self._tileset = TileSet.from_file(Path(path))
        print("## the 3d tile inserting ...")
        # Store tileset.json with added 3dsim_id
        tileset_3dsim_path = self._tileset.root_uri / "tileset_3dsim.json"
        with tileset_3dsim_path.open("w") as f:
            f.write(json.dumps(_tileset_dict, separators=(",", ":"), indent=2, ensure_ascii=False))
        # Upload data to MinIO
        prefix = "public/3dtiles/" + os.path.basename(self._tileset.root_uri) 
        ThreeDSIMBase.minio_client.upload_folder(folder_path=self._tileset.root_uri, prefix=prefix)
        # Parse data information into a database
        self._convert_3dtiles_to_fact(self._tileset.root_tile) # We force the root Tile to be a Scene
        print("## the 3d tile inserted")



    '''
    convert tileset to a fact
    '''
    def _convert_3dtiles_to_fact(self, asset:Tile) -> dict:
        sceneAsset  = template_scene_asset.copy()
        identifier = {
            "_id": self._tileset.extras['3dsim_id']
        }
        sceneAsset.update(identifier)
        adeOfMetadata = self._compute_adeOfMetadata_value(asset, isRoot=True)
        dimensions = self._compute_dimension_value(asset, adeOfMetadata,isRoot=True)
        sceneAsset.update(adeOfMetadata)
        sceneAsset.update(dimensions)
        attibutes = self._compute_attributes_value_for_scene(asset, adeOfMetadata, isRoot=True)
        sceneAsset.update(attibutes)
        ThreeDSIMBase.mongodb_client.add_document("3DSceneFact",sceneAsset)
        if asset.children:
            self._convert_tile_to_fact(asset, fatherID=identifier)
        elif asset.has_content():
            self._convert_content_to_fact(asset,fatherID=identifier)
        elif asset.has_contents():
            self._convert_contents_to_fact(asset,fatherID=identifier)
        else:
            raise Exception("The asset has no children, content or contents.")


    '''
    convert tile to a fact
    '''    
    def _convert_tile_to_fact(self, asset: Tile, fatherID: dict={}):
        sceneAsset = template_scene_asset.copy()
        identifier = {
            "_id": asset.extras['3dsim_id']
        }
        sceneAsset.update(identifier)
        adeOfMetadata = self._compute_adeOfMetadata_value(asset)
        dimensions = self._compute_dimension_value(asset, adeOfMetadata)
        sceneAsset.update(adeOfMetadata)
        sceneAsset.update(dimensions)
        attibutes = self._compute_attributes_value_for_scene(asset, adeOfMetadata)
        sceneAsset.update(attibutes)
        ThreeDSIMBase.mongodb_client.add_document("3DSceneFact",sceneAsset)
        # create the scene-2-scene edge
        asset_edge = self._compute_edge_fact(asset, fatherID, identifier, type=1)
        ThreeDSIMBase.mongodb_client.add_document("SceneEdge",asset_edge)
        if asset.children:
            for child_tile in asset.children:
                if child_tile.children:
                    self._convert_tile_to_fact(child_tile, fatherID=identifier)
                elif child_tile.has_content():
                    self._convert_content_to_fact(child_tile, fatherID=identifier)
                elif child_tile.has_contents():
                    self._convert_contents_to_fact(child_tile, fatherID=identifier)
                else:
                    raise Exception("The asset has no children, content or contents.")
        elif asset.has_content():
            self._convert_content_to_fact(asset, fatherID=identifier)
        elif asset.has_contents():
            self._convert_contents_to_fact(asset, fatherID=identifier)
        else:
            raise Exception("The asset has no children, content or contents.")


    '''
    convert content to a fact
    '''
    def _convert_content_to_fact(self, asset: Tile, fatherID: dict={}):
        modelAsset = template_model_asset.copy()
        identifier = {
            "_id": asset.content.extras['3dsim_id']
        }
        modelAsset.update(identifier)
        adeOfMetadata = self._compute_adeOfMetadata_value(asset)
        dimensions = self._compute_dimension_value(asset, adeOfMetadata)
        modelAsset.update(adeOfMetadata)
        modelAsset.update(dimensions)
        attibutes = self._compute_attributes_value_for_model(asset, adeOfMetadata)
        modelAsset.update(attibutes)
        instance = self._compute_instance_value_for_model(asset.content)
        modelAsset.update(instance)
        ThreeDSIMBase.mongodb_client.add_document("3DModelFact",modelAsset)
        # create the scene-2-model edge
        asset_edge = self._compute_edge_fact(asset, fatherID, identifier, type=2)
        ThreeDSIMBase.mongodb_client.add_document("SceneEdge",asset_edge)

    '''
    convert contents to facts
    '''
    def _convert_contents_to_fact(self, asset: Tile, fatherID: dict={}):
        modelAsset = template_model_asset.copy()
        adeOfMetadata = self._compute_adeOfMetadata_value(asset, isRoot=True)
        dimensions = self._compute_dimension_value(asset, adeOfMetadata)
        modelAsset.update(adeOfMetadata)
        modelAsset.update(dimensions)
        attibutes = self._compute_attributes_value_for_model(asset, adeOfMetadata)
        modelAsset.update(attibutes)
        for content in asset.contents:
            identifier = {
            "_id": content.extras['3dsim_id']
            }
            modelAsset.update(identifier)
            instance = self._compute_instance_value_for_model(content)
            modelAsset.update(instance)
            ThreeDSIMBase.mongodb_client.add_document("3DModelFact",modelAsset)
            # create the scene-2-model edge
            asset_edge = self._compute_edge_fact(asset, fatherID, identifier, type=2)
            ThreeDSIMBase.mongodb_client.add_document("SceneEdge",asset_edge)
        

    '''
    compute the adeOfMetadata 
    '''
    def _compute_adeOfMetadata_value(self, asset: Tile, isRoot: bool=False)->dict:
        if isRoot:
            ade1 = {
                "asset": self._tileset.asset.to_dict()
            }
            ade2 = self._compute_adeOfMetadata_value(asset)
            ade1.update(ade2)
            return {
                "adeOfMetadata":ade1
            }
        else:
            adeOfMetadata = {}
            # TODO: parser meatadata of each tile
            return {
                "adeOfMetadata":adeOfMetadata
            }
    
    '''
    compute the dimension value
    '''
    def _compute_dimension_value(self, asset: Tile, adeOfMetadata: dict, isRoot: bool=False)->dict:
        dimensions = {}
        bv = self._compute_bounding_volume(asset)# get the standard bounding volume
        spatialDV = self._compute_spatial_dimension_value(bv)# get the spatial dimension value
        dimensions.update(spatialDV)
        prodcutDV = self._compute_product_dimension_value(isRoot)# get the product dimension value
        dimensions.update(prodcutDV)
        timeDV = self._compute_time_dimension_value(adeOfMetadata)# get the time dimension value
        dimensions.update(timeDV)
        featureDV = self._compute_feature_dimension_value(adeOfMetadata)# get the feature dimension value
        dimensions.update(featureDV)
        viewpointDV = self._compute_viewpoint_dimension_value(asset)# get the viewpoint dimension value
        dimensions.update(viewpointDV)
        return dimensions        
    
    '''
    compute sptatial dimension value
    '''
    def _compute_spatial_dimension_value(self, bv: dict) -> dict:
        aabb = BoundingVolume.convert_standardBV_to_standardAABB(bv) # convert to standard AABB
        min_x, min_y, min_z, max_x, max_y, max_z = aabb["boundingVolume"]["bv"]
        query_sql = f"""
        SELECT "gridCode" 
        FROM public."SpatialDimension" 
        WHERE "gridExtent" && ST_MakeEnvelope({min_x}, {min_y}, {max_x}, {max_y}, 4326);
        """ # query SQL
        result = ThreeDSIMBase.postgres.execute_sql_with_return_all(query_sql)
        spatial_dimension_values = [row[0] for row in result]
        return {
            "spatialDimension": spatial_dimension_values
        }
    
    
    '''
    compute product dimension value
    '''
    def _compute_product_dimension_value(self, isRoot: bool=False) -> dict:
        product_type = '3DTiles' if isRoot else '3DTiles_Part'
        query = "SELECT \"productClass\" FROM public.\"ProductDimension\" WHERE \"productType\" = %s;"
        result = ThreeDSIMBase.postgres.execute_sql_with_return_one(query, (product_type,))
        if result:
            return {
                "productDimension": result
            }
        else:
            raise Exception("Product class not found for product type: 3DTiles")


    '''
    compute time dimension value
    '''
    def _compute_time_dimension_value(self, adeOfMetadata: dict) -> dict:
        time = ''
        if self._createTime:
            time = self._createTime
        elif self._check_dict_field(adeOfMetadata, 'time'):
            time = '20230105'  # TODO
        return {"timeDimension": time}
    

    '''
    compute feature dimension value
    '''
    def _compute_feature_dimension_value(self, adeOfMetadata: dict) -> dict:
        feature = ''

        if self._featureType:
            feature = self._featureType
        elif self._check_dict_field(adeOfMetadata, 'feature'):
            feature = 'Building'  # TODO

        query = f"SELECT \"FeatureClass\" FROM public.\"FeatureDimension\" WHERE \"FeatureName\" = '{feature}';"
        result = ThreeDSIMBase.postgres.execute_sql_with_return_one(query)

        if result :
            feature_class = result
            return {"featureDimension": feature_class}
        else:
            print("Feature class not found for feature:", feature, "FeatureDimension is set to null!!!")
            return {"featureDimension": ''}
        

    '''
    compute viewpoint dimension value
    '''
    def _compute_viewpoint_dimension_value(self, asset: Tile) -> dict:
        distance = RangeConverter.convert(value= asset.geometric_error, mode_from= RangeMode.GEOMETRIC_ERROR, mode_to=RangeMode.DISTANCE_FROM_EYE_POINT)
        # Query the viewpoint dimension data for the corresponding distance
        query = f"SELECT \"viewPointLevel\" FROM public.\"ViewpointDimension\" " \
                f"WHERE {distance}::numeric BETWEEN \"renderingRangeFrom\"::numeric AND \"renderingRangeTo\"::numeric " \
                f"ORDER BY \"renderingRangeTo\" ASC LIMIT 1;"
        result = ThreeDSIMBase.postgres.execute_sql_with_return_one(query)
        
        if result:
            view_point_level = result
            return {"viewpointDimension": str(view_point_level)}
        else:
            # If the distance is greater than the last row's renderingRangeTo, return the last viewPointLevel
            query = "SELECT \"viewPointLevel\" FROM public.\"ViewpointDimension\" " \
                    "ORDER BY \"renderingRangeTo\" DESC LIMIT 1;"
            result = ThreeDSIMBase.postgres.execute_sql_with_return_one(query)
            
            if result:
                view_point_level = result
                print("Viewpoint level not found for distance:", distance, "Returning the last level:", view_point_level)
                return {"viewpointDimension": str(view_point_level)}
            else:
                print("## Error: ViewpointDimension table is empty!")
                return {"viewpointDimension": 0}
    


    '''
    compute the atrributes of the scene
    '''
    def _compute_attributes_value_for_scene(self, asset: Tile, adeOfMetadata: dict, isRoot: bool = False)->dict:
        attributes = {}
        genericName = self._compute_genericname(adeOfMetadata,isRoot) # genericName
        attributes.update(genericName)
        boundingVolume = self._compute_bounding_volume(asset)# get the standard bounding volume
        attributes.update(boundingVolume)
        transformToWorld = self._compute_transform_toWorld_value(asset)
        attributes.update(transformToWorld)
        creationDate = {"creationDate": self._createTime}
        attributes.update(creationDate)
        validTimeSpan = {"validTimeSpan": [self._validTime[0], self._validTime[1]]}
        attributes.update(validTimeSpan)
        return attributes
    
    '''
    compute the atrributes of the model
    '''
    def _compute_attributes_value_for_model(self, asset: Tile, adeOfMetadata: dict, isRoot: bool = False)->dict:
        attributes = {}
        genericName = self._compute_genericname(adeOfMetadata,isRoot) # genericName
        attributes.update(genericName)
        boundingVolume = self._compute_bounding_volume(asset)# get the standard bounding volume
        attributes.update(boundingVolume)
        transformToWorld = self._compute_transform_toWorld_value(asset)
        attributes.update(transformToWorld)
        creationDate = {"creationDate": self._createTime}
        attributes.update(creationDate)
        validTimeSpan = {"validTimeSpan": [self._validTime[0], self._validTime[1]]}
        attributes.update(validTimeSpan)
        return attributes


    '''
    compute the edgeFact
    '''
    def _compute_edge_fact(self, asset: Tile, fatherID: dict, childID:dict, type: int)->dict:
        asset_edge = template_asset_edge.copy()
        transfrom = self._compute_transform_value(asset)
        asset_edge["type"] = type # 1:scene 2 scene ; 2:scene 2 model
        asset_edge["fromID"] = fatherID["_id"]
        asset_edge["toID"] = childID["_id"]    
        asset_edge["range"] = {
            "renderRange": asset.geometric_error, 
            "rangeMode": "GE"
        }         
        asset_edge.update(transfrom)
        return asset_edge
    
    

    '''
    compute the instance atrribute
    '''    
    def _compute_instance_value_for_model(self,asset: Content)->dict:
        suffix = asset.content_uri.suffix
        tile_url = os.path.abspath(os.path.join(self._tileset.root_uri, asset.content_uri))
        object_name = tile_url.replace("/home/program/3dsim/data/", "/public/")
        return {
            "instance": {
                "filePath": object_name,
                "fileType": suffix # the type of model file, i.e., file suffix
            }
        }
    

    '''
    compute the bounding_volume
    '''
    def _compute_bounding_volume(self, asset: Tile)->dict:
        if asset.bounding_volume is not None:
            boundingVolumeType = list(asset.bounding_volume.to_dict().keys())[0]
            boundingVolume = list(asset.bounding_volume.to_dict().values())[0] 
            if boundingVolumeType == "box":
                return BoundingVolume.convert_3dtilesBV_to_standardBV(InputBVType.Box_3dtiles, boundingVolume)
            elif boundingVolumeType == "region":
                return BoundingVolume.convert_3dtilesBV_to_standardBV(InputBVType.Region_3dtiles,boundingVolume)
            elif boundingVolumeType == "sphere":
                return BoundingVolume.convert_3dtilesBV_to_standardBV(InputBVType.Sphere_3dtiles,boundingVolume)
            else:
                raise Exception("boundingVolumeType is None.")
        else:
            return {}
        
    
    '''
    compute the transform value
    '''
    def _compute_transform_value(self, asset: Tile)->dict:
        if asset.transform is not None:
            return Transform(asset.transform).to_dict()
        else:
            return {"transform": []}
        
    
    '''
    compute the transformToWorld value
    '''
    def _compute_transform_toWorld_value(self, asset: Tile)->dict:
        # TODO
        # all of the tileset have been transformed to the world coordinate system
        return {"transformToWorld": []}
        

    '''
    compute the genericName
    '''
    def _compute_genericname(self, adeOfMetadata : dict, isRoot: bool = False)->dict:
        genericName=''
        parent_folder = os.path.basename(self._tileset.root_uri)
        if isRoot:
            genericName = parent_folder+"_"+self._featureType #order: filePath -> name in metadata
            if self._check_dict_field(adeOfMetadata, 'feature'):
                pass  
            return {
                "genericName": genericName
            }
        else:
            genericName = parent_folder+"_" + self._featureType + '_part'
            return {
                "genericName": genericName
            }
        

    
    
    '''
    check the key in the dict
    '''
    def _check_dict_field(self, data:dict, key:str)->bool:
        if isinstance(data, dict):
            if key in data:
                return True
            for value in data.values():
                if self._check_dict_field(value, key):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._check_dict_field(item, key):
                    return True
        return False


    '''
    classify the edges by type
    1: scene 2 scene
    2: scene 2 model
    '''
    def _classify_edges_by_type(self, edges: list[dict]):
        scene_edges = []
        model_edges = []
        for edge in edges:
            if edge["type"] == 1:
                scene_edges.append(edge)
            elif edge["type"] == 2:
                model_edges.append(edge)
            else:
                # Handle other types if needed
                pass

        return scene_edges, model_edges
    


    

    
