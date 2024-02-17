from pathlib import Path
from typing import Dict
import numpy as np

from .tileset_parser.tileset import TileSet,Asset
from .tileset_parser.tile import Tile
from .tileset_parser.content import Content
from .tileset_parser.contents import Contents

from rmdb_operations.initial_database import createDataBase
from rmdb_operations.postgres import PostgreSQL
from rmdb_operations.tableparams import *
from rmdb_operations.sql_commonds import *


def insertSpatial(gridCode, gridExtent, addressCode, addressName):
    spatialParams = SpatialTable(gridCode=gridCode, gridExtent=gridExtent, addressCode=addressCode, addressName=addressName).getParams()
    spatialID = dataBaseIn.execute_method(sql=sql_insertSpatialDimension, params=spatialParams, method_name="find_one")
    return spatialID

def insertTime(timeCode, year, month, day):
    timeParams = TimeTable(timeCode=timeCode, year=year, month=month, day=day).getParams()
    timeID = dataBaseIn.execute_method(sql=sql_insertTimeDimension, params=timeParams, method_name="find_one")
    return timeID

def insertProduct(productClass, productType, CRS):
    productParams = ProductTable(productClass=productClass, productType=productType, CRS=CRS).getParams()
    productID = dataBaseIn.execute_method(sql=sql_insertProductionDimension, params=productParams, method_name="find_one")
    return productID

def insertFeature(featureClass, featureName):
    featureParams = FeatureTable(featureClass=featureClass, featureName=featureName).getParams()
    featureID = dataBaseIn.execute_method(sql=sql_insertFeatureDimension, params=featureParams, method_name="find_one")
    return featureID

def insertViewpoint(viewPointLevel, renderingRangeFrom, renderingRangeTo):
    viewpointParams = Viewpoint(viewPointLevel=viewPointLevel, renderingRangeFrom=renderingRangeFrom, renderingRangeTo=renderingRangeTo).getParams()
    viewpointID = dataBaseIn.execute_method(sql=sql_insertViewpointDimension, params=viewpointParams, method_name="find_one")
    return viewpointID

# 递归遍历tileset并存入数据库
def traverseTileforDB(tileList : list[Tile], fromScene, Type) -> None:
    for tile in tileList:
        # TODO here
        # spatialID = insertSpatial()
        # timeID = insertTime()
        # productID = insertProduct()
        # featureID = insertFeature()
        # viewpointID = insertViewpoint()
        spatialID = None
        timeID = None
        productID = None
        featureID = None
        viewpointID = None
        SubSceneParams = SubScene(spatialDimension=spatialID,
                                  timeDimension=timeID,
                                  productDimension=productID,
                                  featureDimension=featureID,
                                  viewpointDimension=viewpointID,
                                  name=tile.extensions.name if tile.extensions is not None else None,
                                  identifier=tile.extensions.identifier if tile.extensions is not None else None,
                                  geometricError=tile.geometric_error,
                                  refine=tile._refine,
                                  boundingVolumeType = list(tile.bounding_volume.to_dict().keys())[0] if tile.bounding_volume is not None else None,
                                  boundingVolume = list(tile.bounding_volume.to_dict().values())[0] if tile.bounding_volume is not None else None,
                                  transform = tile.transform.tolist() if tile.transform is not None else None,
                                  creationDate=tile.extensions.createDate if tile.extensions is not None else None,
                                  validFrom=tile.extensions.validFrom if tile.extensions is not None else None,
                                  validTo=tile.extensions.validTo if tile.extensions is not None else None,
                                  adeOfMetadata=tile.adeOfMetadata).getParams()
        
        toScene = dataBaseIn.execute_method(sql = sql_insertSubSceneAssetFact, params = SubSceneParams, method_name = "find_one")

        scene2SceneParams = Scene2Scene(fromScene=fromScene, toScene=toScene, Type=Type).getParams()
        dataBaseIn.execute_method(sql=sql_insertScene2SceneEdgeFact, params=scene2SceneParams)

        if tile.has_content():
            # TODO here
            # spatialID = insertSpatial()
            # timeID = insertTime()
            # productID = insertProduct()
            # featureID = insertFeature()
            # viewpointID = insertViewpoint()
            spatialID = None
            timeID = None
            productID = None
            featureID = None
            viewpointID = None
            ModelParams = Model(spatialDimension=spatialID,
                                timeDimension=timeID,
                                productDimension=productID,
                                featureDimension=featureID,
                                viewpointDimension=viewpointID,
                                name=tile.content.extensions.name if tile.content.extensions is not None else None,
                                identifier=tile.content.extensions.identifier if tile.content.extensions is not None else None,
                                boundingVolume=list(tile.content.bounding_volume.to_dict().values())[0] if tile.content.bounding_volume is not None else None,
                                boundingVolumeType=list(tile.content.bounding_volume.to_dict().keys())[0] if tile.content.bounding_volume is not None else None,
                                transform=tile.content.transform.tolist() if tile.content.transform is not None else None,
                                creationDate=tile.content.extensions.createDate if tile.content.extensions is not None else None,
                                validFrom=tile.content.extensions.validFrom if tile.content.extensions is not None else None,
                                validTo=tile.content.extensions.validTo if tile.content.extensions is not None else None,
                                adeOfMetadata=tile.content.adeOfMetadata,# TODO
                                filePath=str(tile.content.content_uri)).getParams()
            toModel = dataBaseIn.execute_method(sql=sql_insertModelAssetFact, params=ModelParams, method_name="find_one")

            scene2ModelParams = Scene2Model(fromScene=toScene, toScene=toModel, Type=1).getParams()
            dataBaseIn.execute_method(sql=sql_insertScene2ModelEdgeFact, params=scene2ModelParams)
        elif tile.has_contents():
            SubSceneParams = SubScene().getParams()
            toscene = dataBaseIn.execute_method(sql=sql_insertSubSceneAssetFact, params=SubSceneParams, method_name="find_one")
            scene2SceneParams = Scene2Scene(fromScene=toScene, toScene=toscene,Type=1).getParams()
            dataBaseIn.execute_method(sql=sql_insertScene2SceneEdgeFact, params=scene2SceneParams)

            # fromScene = toscene

            for content in tile.contents.content:
                # TODO here
                # spatialID = insertSpatial()
                # timeID = insertTime()
                # productID = insertProduct()
                # featureID = insertFeature()
                # viewpointID = insertViewpoint()
                spatialID = None
                timeID = None
                productID = None
                featureID = None
                viewpointID = None
                ModelParams = Model(spatialDimension=spatialID,
                                    timeDimension=timeID,
                                    productDimension=productID,
                                    featureDimension=featureID,
                                    viewpointDimension=viewpointID,
                                    name=content.extensions.name if content.extensions is not None else None,
                                    identifier=content.extensions.identifier if content.extensions is not None else None,
                                    boundingVolume=list(content.bounding_volume.to_dict().values())[0] if content.bounding_volume is not None else None,
                                    boundingVolumeType=list(content.bounding_volume.to_dict().keys())[0] if content.bounding_volume is not None else None,
                                    transform=content.transform.tolist() if content.transform is not None else None,
                                    creationDate=content.extensions.createDate if content.extensions is not None else None,
                                    validFrom=content.extensions.validFrom if content.extensions is not None else None,
                                    validTo=content.extensions.validTo if content.extensions is not None else None,
                                    adeOfMetadata=content.adeOfMetadata,
                                    filePath=str(content.content_uri)).getParams()
                toModel = dataBaseIn.execute_method(sql=sql_insertModelAssetFact, params=ModelParams, method_name="find_one")

                scene2ModelParams = Scene2Model(fromScene=toscene, toScene=toModel, Type=2).getParams()
                dataBaseIn.execute_method(sql=sql_insertScene2ModelEdgeFact, params=scene2ModelParams)

        if tile.children:
            # 若有孩子结点，则递归遍历
            traverseTileforDB(tile.get_children(), toScene, 1)
        else:
            # 若没有孩子结点，则将toScene设为空
            Scene2SceneParams = Scene2Scene(fromScene=toScene, toScene=None, Type=Type).getParams()
            dataBaseIn.execute_method(sql_insertScene2SceneEdgeFact, Scene2SceneParams)

# 将tileset保存到数据库中
# 参数：tileset_path:文件所在位置，
def saveAsDatabase(tileset_path, database, password, user = None, host = None, port = None):
    # 打开数据库
    global dataBaseIn
    dataBaseIn = createDataBase(database, password, user, host, port)

    # 读取tileset构建TileSet对象
    tileset = TileSet.from_file(Path(tileset_path))

    rootTile = tileset.root_tile
    # TODO here
    spatialID = insertSpatial(gridCode=1, gridExtent=None, addressCode=None, addressName=None)
    # timeID = insertTime()
    # productID = insertProduct()
    # featureID = insertFeature()
    # viewpointID = insertViewpoint()
    timeID = None
    productID = None
    featureID = None
    viewpointID = None
    RootSceneParams = RootScene(spatialDimension=spatialID,
                                timeDimension=timeID,
                                productDimension=productID,
                                featureDimension=featureID,
                                viewpointDimension=viewpointID,
                                name=rootTile.extensions.name if rootTile.extensions is not None else None,
                                identifier=rootTile.extensions.identifier if rootTile.extensions is not None else None,
                                geometricError=rootTile.geometric_error,
                                refine=rootTile._refine,
                                boundingVolumeType = list(rootTile.bounding_volume.to_dict().keys())[0] if rootTile.bounding_volume is not None else None,
                                boundingVolume = list(rootTile.bounding_volume.to_dict().values())[0] if rootTile.bounding_volume is not None else None,
                                transform = rootTile.transform.tolist() if rootTile.transform is not None else None,
                                creationDate=rootTile.extensions.createDate if rootTile.extensions is not None else None,
                                validFrom=rootTile.extensions.validFrom if rootTile.extensions is not None else None,
                                validTo=rootTile.extensions.validTo if rootTile.extensions is not None else None,
                                adeOfMetadata=rootTile.adeOfMetadata).getParams()

    fromScene = dataBaseIn.execute_method(sql = sql_insertRootSceneAssetFact, params = RootSceneParams, method_name = "find_one")
    
    if rootTile.has_content():
        # TODO here
        # spatialID = insertSpatial()
        # timeID = insertTime()
        # productID = insertProduct()
        # featureID = insertFeature()
        # viewpointID = insertViewpoint()
        spatialID = None
        timeID = None
        productID = None
        featureID = None
        viewpointID = None
        ModelParams = Model(spatialDimension=spatialID,
                            timeDimension=timeID,
                            productDimension=productID,
                            featureDimension=featureID,
                            viewpointDimension=viewpointID,
                            name=rootTile.extensions.name if rootTile.extensions is not None else None,
                            identifier=rootTile.extensions.identifier if rootTile.extensions is not None else None,
                            geometricError=rootTile.geometric_error,
                            refine=rootTile._refine,
                            boundingVolume=list(rootTile.content.bounding_volume.to_dict().values())[0] if rootTile.bounding_volume is not None else None,
                            boundingVolumeType=list(rootTile.content.bounding_volume.to_dict().keys())[0] if rootTile.bounding_volume is not None else None,
                            transform=rootTile.transform.tolist() if rootTile.transform is not None else None,
                            creationDate=rootTile.extensions.createDate if rootTile.extensions is not None else None,
                            validFrom=rootTile.extensions.validFrom if rootTile.extensions is not None else None,
                            validTo=rootTile.extensions.validTo if rootTile.extensions is not None else None,
                            adeOfMetadata=rootTile.adeOfMetadata,
                            filePath=str(rootTile.content.content_uri)).getParams()
        
        toModel = dataBaseIn.execute_method(sql=sql_insertModelAssetFact, params=ModelParams, method_name="find_one")
        scene2ModelParams = Scene2Model(fromScene=fromScene, toScene=toModel, Type=0).getParams()
        dataBaseIn.execute_method(sql=sql_insertScene2ModelEdgeFact, params=scene2ModelParams)
    
    elif rootTile.has_contents():
            SubSceneParams = SubScene().getParams()
            toscene = dataBaseIn.execute_method(sql=sql_insertSubSceneAssetFact, params=SubSceneParams, method_name="find_one")
            scene2SceneParams = Scene2Scene(fromScene=fromScene, toScene=toscene,Type=0).getParams()
            dataBaseIn.execute_method(sql=sql_insertScene2SceneEdgeFact, params=scene2SceneParams)

            for content in rootTile.contents.content:
                # TODO here
                # spatialID = insertSpatial()
                # timeID = insertTime()
                # productID = insertProduct()
                # featureID = insertFeature()
                # viewpointID = insertViewpoint()
                spatialID = None
                timeID = None
                productID = None
                featureID = None
                viewpointID = None
                ModelParams = Model(spatialDimension=spatialID,
                                    timeDimension=timeID,
                                    productDimension=productID,
                                    featureDimension=featureID,
                                    viewpointDimension=viewpointID,
                                    name=content.extensions.name if content.extensions is not None else None,
                                    identifier=content.extensions.identifier if content.extensions is not None else None,
                                    boundingVolume=list(content.bounding_volume.to_dict().values())[0] if content.bounding_volume is not None else None,
                                    boundingVolumeType=list(content.bounding_volume.to_dict().keys())[0] if content.bounding_volume is not None else None,
                                    transform=content.transform.tolist() if content.transform is not None else None,
                                    creationDate=content.extensions.createDate if content.extensions is not None else None,
                                    validFrom=content.extensions.validFrom if content.extensions is not None else None,
                                    validTo=content.extensions.validTo if content.extensions is not None else None,
                                    adeOfMetadata=content.adeOfMetadata,# TODO
                                    filePath=str(content.content_uri)).getParams()
                toModel = dataBaseIn.execute_method(sql=sql_insertModelAssetFact, params=ModelParams, method_name="find_one")

                scene2ModelParams = Scene2Model(fromScene=toscene, toScene=toModel, Type=2).getParams()
                dataBaseIn.execute_method(sql=sql_insertScene2ModelEdgeFact, params=scene2ModelParams)

    all_tiles = tileset.root_tile.get_children()

    traverseTileforDB(all_tiles, fromScene, 0)

    dataBaseIn.close_connection()


# 将tileset从数据库中读取出来存为json文件
def saveAsFile(target_path, condition, queryParams, database, password, user = None, host= None, port = None):
    global dataBaseOut
    if user is None or host is None or port is None:
        dataBaseOut = PostgreSQL(database = database, password = password)
    else:
        dataBaseOut = PostgreSQL(database = database, user = user, password = password, host = host, port = port)

    rootTileList = queryRootTile(condition=condition, queryParams=queryParams)
    if rootTileList is None:
        rootTileList = queryTile(condition=condition, queryParams=queryParams)

    fromScene = rootTileList[0]

    contentList = dataBaseOut.find_one(sql=sql_getContent, params=(fromScene,))
    if contentList is not None:
        contentUri = contentList[3].replace("\\", "/")
        content = Content(bounding_volume={contentList[0]:contentList[1]}, transform=contentList[2], content_uri=contentUri, metadataPath=contentList[4])
    else:
        content = None

    rootTile = Tile(geometric_error = rootTileList[1], bounding_volume = {rootTileList[4]: rootTileList[3]}, transform = rootTileList[5], refine_mode = rootTileList[2], metadataUri=rootTileList[6])
    if content is not None:
        rootTile.content = content
    

    tilesList = dataBaseOut.find_all(sql = sql_getTileByRootID, params = (fromScene,))
    for tileList in tilesList:
        if tileList[7] == 2:
            tilesList.remove(tileList)
            contentsList = dataBaseOut.find_all(sql=sql_getContent, params=(tileList[0],))
            if contentsList is not None:
                contents = Contents()
                for contentList in contentsList:
                    if contentList is not None:
                        contentUri = contentList[3].replace("\\","/")
                        content = Content(bounding_volume={contentList[0]:contentList[1]}, transform=contentList[2], content_uri=contentUri, metadataPath=contentList[4])
                    else:
                        content = None
                    if content is not None:
                        contents.content.append(content)
                rootTile.contents = contents
    traverseForTileset(tilesList, rootTile, fromScene)

    tileset = TileSet()
    tileset.asset = Asset(version = "1.1")
    tileset.geometric_error = rootTile.geometric_error
    tileset.root_tile = rootTile
    tileset.write_as_json(Path(target_path))

    dataBaseOut.close_connection()

# 递归遍历数据库中每个记录项的孩子结点
def traverseForTileset(tilesList : list[list], rootTile : Tile, fromScene) -> None:
    for tileList in tilesList:
        fromScene = tileList[0]

        contentList = dataBaseOut.find_one(sql=sql_getContent, params=(fromScene,))
        if contentList is not None:
            contentUri = contentList[3].replace("\\", "/")
            content = Content(bounding_volume={contentList[0]:contentList[1]}, transform=contentList[2], content_uri=contentUri, metadataPath=contentList[4])
        else:
            content = None

        tile = Tile(geometric_error = tileList[1], bounding_volume = {tileList[4]:tileList[3]}, transform = tileList[5], refine_mode = tileList[2], metadataUri=tileList[6])
        if content is not None:
            tile.content = content        

        # if fromScene != 'null':
        childrenList = dataBaseOut.find_all(sql_getTileByRootID, params = (fromScene,))
        for tileList in childrenList:
            if tileList[7] == 2:
                childrenList.remove(tileList)
                contentsList = dataBaseOut.find_all(sql=sql_getContent, params=(tileList[0],))
                if contentsList is not None:
                    contents = Contents()
                    for contentList in contentsList:
                        if contentList is not None:
                            contentUri = contentList[3].replace("\\","/")
                            content = Content(bounding_volume={contentList[0]:contentList[1]}, transform=contentList[2], content_uri=contentUri, metadataPath=contentList[4])
                        else:
                            content = None
                        if content is not None:
                            contents.content.append(content)
                    tile.contents = contents
        rootTile.add_child(tile)
        traverseForTileset(childrenList, tile, fromScene)


def queryRootTile(condition, queryParams):
    match condition:
        case "Spqtial":
            tileList = dataBaseOut.find_one(sql=sql_getRootTileBySpatial, params=queryParams)
        case "Time":
            tileList = dataBaseOut.find_one(sql=sql_getRootTileByTime, params=queryParams)
        case "Product":
            tileList = dataBaseOut.find_one(sql=sql_getRootTileByProduct, params=queryParams)
        case "Feature":
            tileList = dataBaseOut.find_one(sql=sql_getRootTileByFeature, params=queryParams)
        case "Viewpoint":
            tileList = dataBaseOut.find_one(sql=sql_getRootTileByViewpoint, params=queryParams)
        case _:
            print("没有该选项")
    
    return tileList

def queryTile(condition, queryParams):
    match condition:
        case "Spqtial":
            tileList = dataBaseOut.find_one(sql=sql_getTileBySpatial, params=queryParams)
        case "Time":
            tileList = dataBaseOut.find_one(sql=sql_getTileByTime, params=queryParams)
        case "Product":
            tileList = dataBaseOut.find_one(sql=sql_getTileByProduct, params=queryParams)
        case "Feature":
            tileList = dataBaseOut.find_one(sql=sql_getTileByFeature, params=queryParams)
        case "Viewpoint":
            tileList = dataBaseOut.find_one(sql=sql_getTileByViewpoint, params=queryParams)
        case _:
            print("没有该选项")
    
    return tileList