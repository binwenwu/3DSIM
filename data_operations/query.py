from datetime import datetime
from bson.objectid import ObjectId

from base.base_3dsim import ThreeDSIMBase

class Query(ThreeDSIMBase):

    def query_rootSceneAsset(self, product: list[str]=['3DTiles','CityGML','OSG', 'I3S'], 
                             spatialExtent: list[float] = [-180, -90, 180, 90],
                             timeSpan: list[str] = ['19000101', '20990101'], 
                             feature: list[str] = ['Building'], viewedRange: list[float] = [0,9999999]) -> list:
        """
        Query the root scene asset such as 3DTiles, CityGML, OSG, I3S
        :param product: product name list,
          such as 3DTiles, CityGML, OSG, I3S;
        :param spatialExtent: minX, minY, maxX, maxY
        :param timeSpan: minT, maxT
        :param feature: feature name list
        :param viewedRange: minRange, MaxRange (Distance from center of object)
        """
        if not spatialExtent or not timeSpan or not feature or not viewedRange or not product:
            raise ValueError("spatialExtent, timeSpan, feature, viewedRange are all required.")
        pro_id = self._query_productDim(product)       
        list_time = self._query_timeDim(timeSpan)
        list_feature = self._query_featureDim(feature)
        list_viewpoint = self._query_viewPointDim(viewedRange)
        list_spatial = self._query_spatialDim(spatialExtent)

        if not pro_id:
            raise ValueError("product list is none.")
        filtered_pro_id = [item for item in pro_id if item.startswith('1')]
        
        query = {
            "productDimension": {"$in": filtered_pro_id},
            "featureDimension": {"$in": list_feature},
            "viewpointDimension": {"$in": list_viewpoint},
            "timeDimension": {"$in": list_time},
            "spatialDimension":  {"$in": list_spatial}
        }

        result_scene = ThreeDSIMBase.mongodb_client.search_documents("3DSceneFact", query)
        return result_scene

    def query_modelAsset(self, product: list[str]=['RasterRelief','PointCloud','PhysicalField', '3DMesh'], 
                             spatialExtent: list[float] = [-180, -90, 180, 90],
                             timeSpan: list[str] = ['19000101', '20990101'], 
                             feature: list[str] = ['Building'], viewedRange: list[float] = [0,9999999])->list:
        """
        Query the model asset such as RasterRelief, PointCloud, PhysicalField, 3DMesh
        Notice: Include the model asset that make up the 3D scene
        :param product: product name list,
          such as RasterRelief, PointCloud, PhysicalField, 3DMesh
        :param spatialExtent: minX, minY, maxX, maxY
        :param timeSpan: minT, maxT
        :param feature: feature name list
        :param viewedRange: minRange, MaxRange (Distance from center of object)
        """

        if not spatialExtent or not timeSpan or not feature or not viewedRange or not product:
            raise ValueError("spatialExtent, timeSpan, feature, viewedRange are all required.")
        pro_id = self._query_productDim(product)       
        list_time = self._query_timeDim(timeSpan)
        list_feature = self._query_featureDim(feature)
        list_viewpoint = self._query_viewPointDim(viewedRange)
        list_spatial = self._query_spatialDim(spatialExtent)

        if not pro_id:
            raise ValueError("product list is none.")
        


        filtered_pro_id = [item for item in pro_id if item.startswith('2')]
        
        query = {
            "productDimension": {"$in": filtered_pro_id},
            "featureDimension": {"$in": list_feature},
            "viewpointDimension": {"$in": list_viewpoint},
            "timeDimension": {"$in": list_time},
            "spatialDimension":  {"$in": list_spatial}
        }

        result_scene = ThreeDSIMBase.mongodb_client.search_documents("3DModelFact", query)
        return result_scene
    
    def query_edges_of_scene(self, scene_id: ObjectId)->list:
        """
        Query the edges of the scene
        :param scene_id: _id of scene
        :return: edges of scene
        """
        query = {
            "fromID": scene_id
        }
        return ThreeDSIMBase.mongodb_client.search_documents("SceneEdge", query)
    
    def query_model_byID(self, model_id: ObjectId)->list:
        """
        Query the model
        :param scene_id: _id of the model
        :return: the model
        """
        query = {
            "_id": model_id
        }
        return ThreeDSIMBase.mongodb_client.search_documents("3DModelFact", query)
   
    def query_scene_byID(self, scene_id: ObjectId)->list:
        """
        Query the scene
        :param scene_id: _id of the scene
        :return: the scene
        """
        query = {
            "_id": scene_id
        }
        return ThreeDSIMBase.mongodb_client.search_documents("3DSceneFact", query)

    def _query_spatialDim(self, spatialExtent: list[float] = []) -> list[str]:
        """
        :param spatialExtent: minX, minY, maxX, maxY
        :return: the gridCodes
        Notice: Query the spatial dimension table based on the specified criteria
        """
        if len(spatialExtent) != 4:
            raise ValueError("spatialExtent should contain exactly 4 elements: minX, minY, maxX, and maxY.")

        min_x, min_y, max_x, max_y = spatialExtent

        # Query the database using the SQL statement
        sql_query_spatial_dimension = """
        SELECT "gridCode"
        FROM public."SpatialDimension"
        WHERE "gridExtent" && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
        """
        params = (min_x, min_y, max_x, max_y)
        result = ThreeDSIMBase.postgres.execute_sql_with_return_all(sql_query_spatial_dimension, params)

        grid_codes = [row[0] for row in result]
        return grid_codes

    def _query_productDim(self, product: list[str] = []) -> list[str]:
        """
        :param product: product name
        :return: productClass of name
        Notice: Query the product dimension table based on the specified criteria
        """
        sql = """
        SELECT "productClass"
        FROM public."ProductDimension"
        WHERE "productType" IN %s
        """
        params = (tuple(product),)
        result = ThreeDSIMBase.postgres.execute_sql_with_return_all(sql, params)
        product_classes = [row[0] for row in result]
        return product_classes

    def _query_featureDim(self, feature: list[str] = []) -> list[str]:
        """
        :param feature: feature name list
        :return: featureClass of name
        Notice: Query the feature dimension table based on the specified criteria
        """
        sql = """
        SELECT "FeatureClass"
        FROM public."FeatureDimension"
        WHERE "FeatureName" IN %s
        """
        params = (tuple(feature),)
        result = ThreeDSIMBase.postgres.execute_sql_with_return_all(sql, params)
        feature_classes = [row[0] for row in result]
        return feature_classes

    def _query_timeDim(self, timeSpan: list[str] = []) -> list[str]:
        """
        :param timeSpan: minT, maxT, such as 19990101, 20220202
        :return: All of time timeCode included in the input span
        Notice: Query the time dimension table based on the specified criteria
        """
        if len(timeSpan) == 0:
            return []
        
        if len(timeSpan) != 2:
            raise ValueError("timeSpan should contain exactly 2 elements: minT and maxT.")

        min_time_str, max_time_str = timeSpan
        min_time = datetime.strptime(min_time_str, "%Y%m%d").date()
        max_time = datetime.strptime(max_time_str, "%Y%m%d").date()

        # Query the database using the SQL statement
        sql_query_time_dimension = """
        SELECT "timeCode"
        FROM public."TimeDimension"
        WHERE "timeCode" BETWEEN %s AND %s
        """
        params = (min_time_str, max_time_str)
        result = ThreeDSIMBase.postgres.execute_sql_with_return_all(sql_query_time_dimension, params)

        time_codes = [row[0] for row in result]
        return time_codes

    def _query_viewPointDim(self, viewedRange: list[float] = []) -> list[str]:
        """
        :param viewedRange: minRange, maxRange (Distance from the center of the object)
        :return: the viewPointLevels (Type: str)
        Notice: Query the viewpoint dimension table based on the specified criteria
        """
        if len(viewedRange) == 0:
            return []
        if len(viewedRange) != 2:
            raise ValueError("viewedRange should contain exactly 2 elements: minRange and maxRange.")

        min_range, max_range = viewedRange

        # Query the database using the SQL statement
        sql_query_viewpoint_dimension = """
        SELECT "viewPointLevel"
        FROM public."ViewpointDimension"
        WHERE "renderingRangeFrom" >= %s AND "renderingRangeTo" <= %s
        """
        params = (min_range, max_range)
        result = ThreeDSIMBase.postgres.execute_sql_with_return_all(sql_query_viewpoint_dimension, params)

        view_point_levels = [str(row[0]) for row in result]
        return view_point_levels

