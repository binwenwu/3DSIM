from datetime import datetime
from bson.objectid import ObjectId
from data_operations.query import Query
from base.base_3dsim import ThreeDSIMBase



class Remove(ThreeDSIMBase):

    def __init__(self):
        self.query = Query()
    
    def remove_rootSceneAsset(self, product: list[str]=['3DTiles','CityGML','OSG', 'I3S'], 
                            spatialExtent: list[float] = [-180, -90, 180, 90],
                            timeSpan: list[str] = ['19000101', '20990101'], 
                            feature: list[str] = ['Building'], viewedRange: list[float] = [0,9999999]):
        """
        Remove root scene assets based on specified criteria.
        :param product: product name list,
        such as 3DTiles, CityGML, OSG, I3S;
        :param spatialExtent: minX, minY, maxX, maxY
        :param timeSpan: minT, maxT
        :param feature: feature name list
        :param viewedRange: minRange, MaxRange (Distance from center of object)
        """
        if not spatialExtent or not timeSpan or not feature or not viewedRange or not product:
            raise ValueError("spatialExtent, timeSpan, feature, viewedRange are all required.")
        
        pro_id = self.query._query_productDim(product)       
        list_time = self.query._query_timeDim(timeSpan)
        list_feature = self.query._query_featureDim(feature)
        list_viewpoint = self.query._query_viewPointDim(viewedRange)
        list_spatial = self.query._query_spatialDim(spatialExtent)

        if not pro_id:
            raise ValueError("product list is none.")
        
        # Filter out product numbers belonging to sceneAsset
        filtered_pro_id = [item for item in pro_id if item.startswith('1')]
        
        query = {
            "productDimension": {"$in": filtered_pro_id},
            "featureDimension": {"$in": list_feature},
            "viewpointDimension": {"$in": list_viewpoint},
            "timeDimension": {"$in": list_time},
            "spatialDimension":  {"$in": list_spatial}
        }

        result_scene = ThreeDSIMBase.mongodb_client.remove_documents("3DSceneFact", query)
        return result_scene



    def remove_modelAsset(self, product: list[str]=['RasterRelief','PointCloud','PhysicalField', '3DMesh'], 
                        spatialExtent: list[float] = [-180, -90, 180, 90],
                        timeSpan: list[str] = ['19000101', '20990101'], 
                        feature: list[str] = ['Building'], viewedRange: list[float] = [0,9999999]):
        """
        Remove model assets based on specified criteria.
        :param product: product name list,
        such as RasterRelief, PointCloud, PhysicalField, 3DMesh
        :param spatialExtent: minX, minY, maxX, maxY
        :param timeSpan: minT, maxT
        :param feature: feature name list
        :param viewedRange: minRange, MaxRange (Distance from center of object)
        """
        if not spatialExtent or not timeSpan or not feature or not viewedRange or not product:
            raise ValueError("spatialExtent, timeSpan, feature, viewedRange are all required.")
        
        pro_id = self.query._query_productDim(product)       
        list_time = self.query._query_timeDim(timeSpan)
        list_feature = self.query._query_featureDim(feature)
        list_viewpoint = self.query._query_viewPointDim(viewedRange)
        list_spatial = self.query._query_spatialDim(spatialExtent)

        if not pro_id:
            raise ValueError("product list is none.")
        

        # Filter out product numbers belonging to modelAsset
        filtered_pro_id = [item for item in pro_id if item.startswith('2')]
        
        query = {
            "productDimension": {"$in": filtered_pro_id},
            "featureDimension": {"$in": list_feature},
            "viewpointDimension": {"$in": list_viewpoint},
            "timeDimension": {"$in": list_time},
            "spatialDimension":  {"$in": list_spatial}
        }

        result_scene = ThreeDSIMBase.mongodb_client.remove_documents("3DModelFact", query)
        return result_scene



    def remove_edges_of_scene(self, scene_id: ObjectId):
        """
        Remove the edges of the specified scene.
        :param scene_id: _id of scene
        """
        query = {
            "fromID": scene_id
        }
        return ThreeDSIMBase.mongodb_client.remove_documents("SceneEdge", query)
    

    def delete_model_byID(self, model_id: ObjectId):
        """
        Delete the model based on its ID.
        :param model_id: _id of the model to be deleted
        """
        query = {
            "_id": model_id
        }
        ThreeDSIMBase.mongodb_client.remove_documents("3DModelFact", query)

    
    def delete_scene_byID(self, scene_id: ObjectId):
        """
        Delete the scene based on its ID.
        :param scene_id: _id of the scene to be deleted
        """
        query = {
            "_id": scene_id
        }
        ThreeDSIMBase.mongodb_client.remove_documents("3DSceneFact", query)







