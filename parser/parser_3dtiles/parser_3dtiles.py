import os
from pathlib import Path
from typing import Optional, Tuple

from base.bounding_volume import BoundingVolume, InputBVType
from base.type import Transform
from tools.render_range_convert import RangeMode, RangeConverter

from base.base_3dsim import ThreeDSIMBase
from rmdb_operations.sql_commonds import *
from mongodb_operations.mongo_template import template_scene_asset, template_asset_edge, template_model_asset
from mongodb_operations.mongodb import MongoDB
from tools.query import Query

from .tile3d_parser.tileset_parser.tileset import TileSet,Asset
from .tile3d_parser.tileset_parser.tile import Tile
from .tile3d_parser.tileset_parser.content import Content
from .tile3d_parser.tileset_parser.contents import Contents

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

    # parse a3dtile instance file and insert it into 3dsim
    def add_data(self, path:str, featureType: str='', 
                 createTime: str='', validTime: list[str]=['',''])->None:
        self._featureType = featureType
        self._createTime = createTime
        self._validTime = validTime
        self._tileset = TileSet.from_file(Path(path))

        print("## the 3d tile inserting ...")
        self._convert_tile_to_fact(self._tileset.root_tile, isRoot=True)
        print("## the 3d tile inserted")

    # save the 3d scene asset to 3dtiles JSON
    def save_data_to3dtiles(self, sceneAsset: dict, path:str, query: Query)->None:
        self._counter_subscenes = 0 
        self._counter_submodels = 0
        root_p = get_endpoint_minio()+ThreeDSIMBase.minio_client.bucket_name+'/'

        # for root tile
        r_bv = BoundingVolume.convert_standardBV_to_3dtiles(sceneAsset['boundingVolume'])
        r_transf = Transform.from_dict_worldT(sceneAsset).matrix
        root_tile = Tile(bounding_volume = r_bv, transform=r_transf)
        # get the childs 
        edges = query.query_edges_of_scene(sceneAsset['_id'])
        edge_scene, edge_model = self._classify_edges_by_type(edges)
        if len(edge_model) == 1:# for content and contents
            model = query.query_model_byID(edge_model[0]['toID'])[0]
            c_bv = BoundingVolume.convert_standardBV_to_3dtiles(model['boundingVolume'])
            c_uri = root_p+model['instance']['filePath']
            # c_meta = model['adeOfMetadata']
            c_transf = Transform.from_dict(edge_model[0]).matrix
            root_tile.content= Content(bounding_volume=c_bv, 
                transform=c_transf, content_uri=c_uri)
            self._counter_submodels +=1
        elif len(edge_model) >= 1:
            contents = Contents()
            for edge in edge_model:
                model = query.query_model_byID(edge['toID'])[0]
                c_bv = BoundingVolume.convert_standardBV_to_3dtiles(model['boundingVolume'])
                c_uri = root_p+model['instance']['filePath']
                # c_meta = model['adeOfMetadata']
                c_transf = Transform.from_dict(edge).matrix
                c2 = Content(bounding_volume=c_bv, 
                    transform=c_transf, content_uri=c_uri)
                contents.content.append(c2)
                self._counter_submodels +=1
            root_tile.contents = contents
        if len(edge_scene) != 0:# for children
            children = []
            for edge in edge_scene:
                til = self._get_tile(query=query, edge=edge)
                children.append(til)
                self._counter_subscenes +=1
            root_tile.children = children

        # for tileset
        tileset = TileSet()
        tileset.asset = Asset(version = "1.0")
        tileset.root_uri = root_p
        tileset.root_tile = root_tile
        tileset.geometric_error = root_tile.geometric_error
        tileset.write_as_json(Path(path))
        print(f"This 3dtiles have {self._counter_subscenes} sub scenes, and {self._counter_submodels} sub models")
        pass
    
    def _get_tile(self, query:Query, edge:dict)->Tile:
        root_p = get_endpoint_minio()+ThreeDSIMBase.minio_client.bucket_name+'/'
        if edge["type"] != 1:
            raise ValueError("the edge type is not 1")
        scene = query.query_scene_byID(edge['toID'])[0]
        s_bv = BoundingVolume.convert_standardBV_to_3dtiles(scene['boundingVolume'])
        s_transf = Transform.from_dict(edge).matrix
        s_ge = edge['range']['renderRange']

        tile = Tile(bounding_volume = s_bv, transform=s_transf, geometric_error=s_ge)

        # s_meta = scene['adeOfMetadata']
        if edge['range']['rangeMode'] != 'GE':
            print("TODO: convert to GE not yet")
            raise ValueError("RangeMode is not GE")
        
        # get the childs 
        edges_child = query.query_edges_of_scene(scene['_id'])
        edge_scene, edge_model = self._classify_edges_by_type(edges_child)
        # for content and contents
        if len(edge_model) == 1:
            model = query.query_model_byID(edge_model[0]['toID'])[0]
            c_bv = BoundingVolume.convert_standardBV_to_3dtiles(model['boundingVolume'])
            c_uri = root_p+ model['instance']['filePath']
            # c_meta = model['adeOfMetadata']
            c_transf = Transform.from_dict(edge_model[0]).matrix
            s_content= Content(bounding_volume=c_bv, 
                transform=c_transf, content_uri=c_uri)
            tile.content =  s_content
            self._counter_submodels +=1
        elif len(edge_model) >= 1:
            s_contents = Contents()
            for edge_m in edge_model:
                model = query.query_model_byID(edge_m['toID'])[0]
                c_bv = BoundingVolume.convert_standardBV_to_3dtiles(model['boundingVolume'])
                c_uri = root_p+ model['instance']['filePath']
                # c_meta = model['adeOfMetadata']
                c_transf = Transform.from_dict(edge_m).matrix
                c2 = Content(bounding_volume=c_bv, 
                    transform=c_transf, content_uri=c_uri)
                s_contents.content.append(c2)
                self._counter_submodels +=1
            tile.contents = s_contents
            
        # for children
        if len(edge_scene) != 0:
            s_children = []
            for edge_s in edge_scene:
                s_tile = self._get_tile(query, edge_s)
                s_children.append(s_tile)
                self._counter_subscenes +=1
            tile.children = s_children            
        return tile
    
    def remove_data(self, data_item):
        pass

    def search_data(self, search_query):
        pass
    
    def _convert_tile_to_fact(self, tile:Tile, isRoot: bool=False, fatherID: dict={}) -> dict:
        # create the scene asset
        sceneAsset  = template_scene_asset.copy()
        identifier = self._compute_identifier_value()
        sceneAsset.update(identifier)
        adeOfMetadata = self._compute_adeOfMetadata_value(tile, isRoot=isRoot)
        dimensions = self._compute_dimension_value(tile,adeOfMetadata,isRoot=isRoot)
        sceneAsset.update(adeOfMetadata)
        sceneAsset.update(dimensions)
        attibutes = self._compute_attributes_value(tile, adeOfMetadata, isRoot)
        sceneAsset.update(attibutes)
        # print(sceneAsset)

        ThreeDSIMBase.mongodb_client.add_document("3DSceneFact",sceneAsset)

        if not isRoot:       
            # create the scene-2-scene edge
            assetEdge = template_asset_edge.copy()
            edge = self._compute_edge_fact_for_s2s(tile, fatherID=fatherID, childID=identifier)
            assetEdge.update(edge)
            # print(assetEdge)
            ThreeDSIMBase.mongodb_client.add_document("SceneEdge",assetEdge)
        else:
            pass
        
        if tile.children: # child tiles
            for child in tile.get_children():
                self._convert_tile_to_fact(child, fatherID=identifier)
        else:
            pass # no child tile 
        
        if tile.has_content():#content
            # create the model asset
            content = tile.content
            bv_father={"boundingVolume":sceneAsset['boundingVolume']}
            modelAsset = self._compute_all_values_for_model(content,dimensions, bv_father)
            # print(modelAsset)
            ThreeDSIMBase.mongodb_client.add_document("3DModelFact",modelAsset)

            # create the scene-2-model edge
            scene2model_edge = template_asset_edge.copy()
            identifier_model = {"_id": modelAsset["_id"]}
            edge_model = self._compute_edge_fact_for_s2m(tile, fatherID=identifier, childID=identifier_model,ge=tile.geometric_error)
            scene2model_edge.update(edge_model)
            # print(scene2model_edge)
            ThreeDSIMBase.mongodb_client.add_document("SceneEdge",scene2model_edge) 
        elif tile.has_contents():#contents
            for content2 in tile.contents.content:
                # create the model asset
                bv_father={"boundingVolume":sceneAsset['boundingVolume']}
                modelAsset = self._compute_all_values_for_model(content2,dimensions,bv_father)
                # print(modelAsset)
                ThreeDSIMBase.mongodb_client.add_document("3DModelFact",modelAsset)

                # create the scene-2-model edge
                scene2model_edge = template_asset_edge.copy()
                identifier_model = {"_id": modelAsset["_id"]}
                edge_model = self._compute_edge_fact_for_s2m(tile, fatherID=identifier, childID=identifier_model, ge=tile.geometric_error)
                scene2model_edge.update(edge_model)
                # print(scene2model_edge)
                ThreeDSIMBase.mongodb_client.add_document("SceneEdge",scene2model_edge) 

    # compute all of the dimension value of the tile
    def _compute_dimension_value(self, tile: Tile, adeOfMetadata: dict, isRoot: bool)->dict:
        dimensions = {}
        bv = self._compute_bounding_volume(tile)# get the standard bounding volume
        spatialDV = self._compute_sptail_dimension_value(bv)# get the spatial dimension value
        dimensions.update(spatialDV)
        prodcutDV = self._compute_product_dimension_value(isRoot)# get the product dimension value
        dimensions.update(prodcutDV)
        timeDV = self._compute_time_dimension_value(adeOfMetadata)# get the time dimension value
        dimensions.update(timeDV)
        featureDV = self._compute_feature_dimension_value(adeOfMetadata)# get the feature dimension value
        dimensions.update(featureDV)
        viewpointDV = self._compute_viewpoint_dimension_value(tile)# get the viewpoint dimension value
        dimensions.update(viewpointDV)
        return dimensions
    
    # compute the atrributes of the tile
    def _compute_attributes_value(self, tile: Tile, adeOfMetadata: dict, isRoot: bool = False)->dict:
        sceneAsset = {}
        genericName = self._compute_genericname_value(tile,adeOfMetadata,isRoot) # genericName
        sceneAsset.update(genericName)
        boundingVolume = self._compute_bounding_volume(tile)# get the standard bounding volume
        sceneAsset.update(boundingVolume)
        transformToWorld = self._compute_transform_toWorld_value(tile)
        sceneAsset.update(transformToWorld)
        creationDate = {"creationDate": self._createTime}
        sceneAsset.update(creationDate)
        validTimeSpan = {"validTimeSpan": [self._validTime[0], self._validTime[1]]}
        sceneAsset.update(validTimeSpan)
        return sceneAsset
    
    # compute all of the attributes of the model asset
    def _compute_all_values_for_model(self, model: Content, dimension_scene: dict, bv_father: dict = {})->dict:
        modelAsset  = template_model_asset.copy()
        identifier_model = self._compute_identifier_value()
        modelAsset.update(identifier_model)
        adeOfMetadata = self._compute_adeOfMetadata_value_for_model(model)
        bv = self._compute_bounding_volume(model)# get the standard bounding volume
        if not bv:
            if not bv_father:
                raise Exception("bv and bv_father both are null!")
            bv = bv_father
        modelAsset.update(bv)
        spatialDV = self._compute_sptail_dimension_value(bv)# get the spatial dimension value
        dimension_scene.update(spatialDV)
        prodcutDV = self._compute_product_dimension_for_model(model)# get the product dimension value
        dimension_scene.update(prodcutDV)
        modelAsset.update(adeOfMetadata)
        modelAsset.update(dimension_scene)
        tmp1, tmp2 = os.path.splitext(model.content_uri)
        genericName_model = {"genericName": self._tileset.root_uri.stem + tmp1.replace("\\", "_")}
        modelAsset.update(genericName_model)
        attibutes = self._compute_attributes_value_for_model(model)
        modelAsset.update(attibutes)
        instance = self._compute_instance_value_for_model(model)
        modelAsset.update(instance)
        return modelAsset

     # compute the atrributes of the model
    def _compute_attributes_value_for_model(self, model: Content)->dict:
        modelAsset = {}
        boundingVolume = self._compute_bounding_volume(model)# get the standard bounding volume
        modelAsset.update(boundingVolume)
        transformToWorld = self._compute_transform_toWorld_value(model)
        modelAsset.update(transformToWorld)
        creationDate = {"creationDate": self._createTime}
        modelAsset.update(creationDate)
        validTimeSpan = {"validTimeSpan": [self._validTime[0], self._validTime[1]]}
        modelAsset.update(validTimeSpan)
        return modelAsset

    # compute product dimension value
    def _compute_product_dimension_value(self, isRoot: bool) -> dict:
        product_type = '3DTiles' if isRoot else '3DTiles_Part'
        query = "SELECT \"productClass\" FROM public.\"ProductDimension\" WHERE \"productType\" = %s;"
        result = ThreeDSIMBase.postgres.execute_sql_with_return_one(query, (product_type,))
        if result:
            return {
                "productDimension": result
            }
        else:
            raise Exception("Product class not found for product type: 3DTiles")
    
    def _compute_product_dimension_for_model(self, model: Content) -> dict:
        suffix = model.content_uri.suffix
        if suffix == '.pnts':
            product_type = 'PointCloud'
        else:
            product_type = '3DMesh'
        query = "SELECT \"productClass\" FROM public.\"ProductDimension\" WHERE \"productType\" = %s;"
        result = ThreeDSIMBase.postgres.execute_sql_with_return_one(query, (product_type,))
        if result:
            return {
                "productDimension": result
            }
        else:
            raise Exception("Product class not found for product type: 3DTiles")


    # compute sptatial dimension value
    def _compute_sptail_dimension_value(self, bv: dict) -> dict:
        aabb = BoundingVolume.convert_to_AABB(bv) # convert to standard AABB
        min_x, min_y, min_z, max_x, max_y, max_z = aabb["bv"]
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

    # compute feature dimension value
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

    # compute viewpoint dimension value
    def _compute_viewpoint_dimension_value(self, tile: Tile) -> dict:
        distance = RangeConverter.convert(value= tile.geometric_error, mode_from= RangeMode.GEOMETRIC_ERROR, mode_to=RangeMode.DISTANCE_FROM_EYE_POINT)
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

    # compute time dimension value
    def _compute_time_dimension_value(self, adeOfMetadata: dict) -> dict:
        time = ''
        if self._createTime:
            time = self._createTime
        elif self._check_dict_field(adeOfMetadata, 'time'):
            time = '20230105'  # TODO
        return {"timeDimension": time}
    
    def _compute_bounding_volume(self, tile: Union[Tile, Content])->dict:
        if tile.bounding_volume is not None:
            boundingVolumeType = list(tile.bounding_volume.to_dict().keys())[0]
            boundingVolume = list(tile.bounding_volume.to_dict().values())[0] 
            if boundingVolumeType == "box":
                return BoundingVolume.convert_to_standardBV(InputBVType.Box_3dtile, boundingVolume)
            elif boundingVolumeType == "region":
                return BoundingVolume.convert_to_standardBV(InputBVType.Region_3dtile,boundingVolume)
            elif boundingVolumeType == "sphere":
                return BoundingVolume.convert_to_standardBV(InputBVType.Sphere_3dtile,boundingVolume)
            else:
                raise Exception("boundingVolumeType is None.")
        else:
            return {}
    
    def _compute_transform_value(self, tile: Union[Tile, Content])->dict:
        if tile.transform is not None:
            return Transform(tile.transform).to_dict()
        else:
            return {"transform": []}
        
    def _compute_transform_toWorld_value(self, tile: Union[Tile, Content])->dict:
        # TODO
        # all of the tileset have been transformed to the world coordinate system
        return {"transformToWorld": []}
        
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
    
    # compute the genericName atrribute of the tile
    def _compute_genericname_value(self, tile: Tile, adeOfMetadata : dict, isRoot: bool = False)->dict:
        genericName=''
        parent_folder = os.path.basename(os.path.dirname(self._tileset.root_uri))
        if isRoot:
            genericName = parent_folder+"_"+self._featureType #order: filePath -> name in metadata
            if self._check_dict_field(adeOfMetadata, 'feature'):
                pass  # TODO 是不是要用数据自带的feature字段替代用户输出的featureType？
            return {
                "genericName": genericName
            }
        else:
            genericName = parent_folder+"_"+self._featureType + '_part'
            return {
                "genericName": genericName
            }

    # compute the identifier atrribute of the tile
    def _compute_identifier_value(self)->dict:
        return {
            "_id": ThreeDSIMBase.mongodb_client.getObjectId()
        }   

    #compute the adeOfMetadata value 
    def _compute_adeOfMetadata_value(self, tile: Tile, isRoot: bool)->dict:
        if isRoot:
            return self._compute_adeOfMetadata_value_for_root(self._tileset)
        else:
            return self._compute_adeOfMetadata_value_for_tile(tile)

    # compute the adeOfMetadata value of the root tile
    def _compute_adeOfMetadata_value_for_root(self, tileset: TileSet)->dict:
        adeOfMetadata = {
            "asset": tileset.asset.to_dict()
        }
        ade2 = self._compute_adeOfMetadata_value_for_tile(tileset.root_tile)
        adeOfMetadata.update(ade2)
        return {
            "adeOfMetadata": adeOfMetadata
        }
    
    # compute the adeOfMetadata value of the tile
    def _compute_adeOfMetadata_value_for_tile(self, tile: Tile)->dict:
        adeOfMetadata = {}
        # TODO: parser meatadata of each tile
        return adeOfMetadata
    
    # compute the adeOfMetadata value of the content
    def _compute_adeOfMetadata_value_for_model(self, model: Content)->dict:
        adeOfMetadata = {}
        # TODO: parser meatadata of each content
        return adeOfMetadata
    
    # compute the edgeFact
    def _compute_edge_fact_for_s2s(self, asset: Tile, fatherID: dict, childID:dict)->dict:
        edgeFact = {}
        transfrom = self._compute_transform_value(asset)
        edgeFact["type"] = 1 # 1:scene 2 scene; 2: scene 2 model
        edgeFact["fromID"] = fatherID["_id"]
        edgeFact["toID"] = childID["_id"]    
        edgeFact["range"] = {
            "renderRange": asset.geometric_error, 
            "rangeMode": "GE"
        }         
        edgeFact.update(transfrom)
        return edgeFact
    
    def _compute_edge_fact_for_s2m(self, asset: Content, fatherID: dict, childID:dict, ge:float)->dict:
        edgeFact = {}
        transfrom = self._compute_transform_value(asset)
        edgeFact["type"] = 2 # 1:scene 2 scene; 2: scene 2 model
        edgeFact["fromID"] = fatherID["_id"]
        edgeFact["toID"] = childID["_id"]    
        edgeFact["range"] = {
            "renderRange": ge, 
            "rangeMode": "GE"
        }         
        edgeFact.update(transfrom)
        return edgeFact
    
    def _compute_instance_value_for_model(self,model: Content)->dict:
        suffix = model.content_uri.suffix
        hash_tileset_8 = generate_short_hash(input_string=self._tileset.root_uri.as_posix(), length=5)
        tile_url = os.path.abspath(os.path.join(self._tileset.root_uri, model.content_uri))
        tile_url_base = os.path.splitext(tile_url)[0]
        hash_tile_32 = generate_short_hash(input_string=tile_url_base, length=32)
        object_name = "public/3dtiles/" + hash_tileset_8 + "/" + hash_tile_32 + suffix
        ThreeDSIMBase.minio_client.upload_file(file_name=tile_url, object_name=object_name)
        return {
            "instance": {
                "filePath": object_name,
                "fileType": suffix # the type of model file, i.e., file suffix
            }
        }
 
    
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
