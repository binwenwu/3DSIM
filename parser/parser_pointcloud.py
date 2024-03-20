import os
from base.base_3dsim import ThreeDSIMBase
from mongodb_operations.mongo_template import template_model_asset_pointcloud
from .base.Transform import Transform
from .base.type import ModelAsset, PointCloudType
import laspy
from .base.bounding_volume import BoundingVolume
import numpy as np


class ParserPointcloud(ThreeDSIMBase):
    def __init__(self)-> None:
        super().__init__()
        self._createTime = ''
        self._validTime = []
        self._mimeType = '' 
        self._uri = ''

    # parse a point cloud asset instance file and insert it into 3dsim
    def add_data(self, mimeType: str,  path:str, 
                 createTime: str='', validTime: list[str]=['',''])->None:
        self._createTime = createTime
        self._validTime = validTime
        self._mimeType = mimeType
        self._uri = path

        print("## the point clond inserting ...")
        self._convert_pointCloud_to_fact()
        print("## the point clond field inserted")
    

    def _convert_pointCloud_to_fact(self)->None:
        pointCloudAsset  = template_model_asset_pointcloud.copy() 

        if self._mimeType == PointCloudType.LAS.value:
            self._read_las(pointCloudAsset)
        elif self._mimeType == PointCloudType.LAZ.value:
            self._read_laz(pointCloudAsset)
        elif self._mimeType == PointCloudType.XYZ.value:
            self._read_xyz(pointCloudAsset)
        else:
            raise ValueError("the pointCloud type is not supported currently")
         
        identifier = self._compute_identifier_value()
        pointCloudAsset.update(identifier)
        self._compute_dimension_value(pointCloudAsset)
        self._compute_attributes_value(pointCloudAsset)
        
        ThreeDSIMBase.mongodb_client.add_document("3DModelFact",pointCloudAsset)
        print(pointCloudAsset)


    def _read_las(self, asset: dict)->None:
        las = laspy.read(self._uri)
        x_min = las.header.x_min
        x_max = las.header.x_max
        y_min = las.header.y_min
        y_max = las.header.y_max
        z_min = las.header.z_min
        z_max = las.header.z_max
        bv = BoundingVolume.convert_to_standardAABB(y_min, x_min, y_max, x_max, z_min, z_max)
        asset.update(bv)

    def _read_laz(self, asset: dict)->None:
        laz = laspy.read(self._uri)
        x_min = laz.header.x_min
        x_max = laz.header.x_max
        y_min = laz.header.y_min
        y_max = laz.header.y_max
        z_min = laz.header.z_min
        z_max = laz.header.z_max
        bv = BoundingVolume.convert_to_standardAABB(y_min, x_min, y_max, x_max, z_min, z_max)
        asset.update(bv)
    

    def _read_xyz(self, asset: dict)->None:
        with open(self._uri, 'r') as file:
            lines = file.readlines()
            data = np.array([list(map(float, line.split())) for line in lines])
        min_xyz = np.min(data, axis=0)
        max_xyz = np.max(data, axis=0)
        bv = BoundingVolume.convert_to_standardAABB(min_xyz[0], min_xyz[1], max_xyz[0], max_xyz[1], min_xyz[2], max_xyz[2])
        asset.update(bv)

    # compute the identifier atrribute of the tile
    def _compute_identifier_value(self)->dict:
        return {
            "_id": ThreeDSIMBase.mongodb_client.getObjectId()
        }   
    
    # compute all of the dimension value of the tile
    def _compute_dimension_value(self, asset: dict)->None:
        spatialDV = self._compute_spatial_dimension_value(asset["boundingVolume"])# get the spatial dimension value
        asset.update(spatialDV)
        prodcutDV = self._compute_product_dimension_value()# get the product dimension value
        asset.update(prodcutDV)
        timeDV = self._compute_time_dimension_value()# get the time dimension value
        asset.update(timeDV)
        featureDV = self._compute_feature_dimension_value()# get the feature dimension value
        asset.update(featureDV)
        viewpointDV = self._compute_viewpoint_dimension_value()# get the viewpoint dimension value
        asset.update(viewpointDV)


    # compute sptatial dimension value
    def _compute_spatial_dimension_value(self, aabb: dict) -> dict:
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

    def _compute_product_dimension_value(self) -> dict:
        product_type = 'PointCloud'
        query = "SELECT \"productClass\" FROM public.\"ProductDimension\" WHERE \"productType\" = %s;"
        result = ThreeDSIMBase.postgres.execute_sql_with_return_one(query, (product_type,))
        if result:
            return {
                "productDimension": result
            }
        else:
            raise Exception("Product class not found for product type: PointCloud")
    
    # compute time dimension value
    def _compute_time_dimension_value(self) -> dict:
        time = ''
        if self._createTime:
            time = self._createTime
        return {"timeDimension": time}
    
    # compute feature dimension value
    def _compute_feature_dimension_value(self) -> dict:
        feature = 'Building'
        query = f"SELECT \"FeatureClass\" FROM public.\"FeatureDimension\" WHERE \"FeatureName\" = '{feature}';"
        result = ThreeDSIMBase.postgres.execute_sql_with_return_one(query)
        if result :
            feature_class = result
            return {"featureDimension": feature_class}
        else:
            print("Feature class not found for feature:", feature, "FeatureDimension is set to null!!!")
            return {"featureDimension": ''}
        
    # compute viewpoint dimension value
    def _compute_viewpoint_dimension_value(self) -> dict:
        # Query the viewpoint dimension data for the corresponding distance
        distance = 1000
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

    # compute the atrributes of the point cloud
    def _compute_attributes_value(self, asset: dict)->None:
        genericName = self._compute_genericname_value() # genericName
        asset.update(genericName)
        creationDate = {"creationDate": self._createTime}
        asset.update(creationDate)
        validTimeSpan = {"validTimeSpan": [self._validTime[0], self._validTime[1]]}
        asset.update(validTimeSpan)
        objectInstance = self._compute_instance_value_for_model()
        asset.update(objectInstance)
    
    # compute the genericName atrribute
    def _compute_genericname_value(self)->dict:
        genericName = os.path.basename(self._uri)

        return {
            "genericName": genericName
        }

    def _compute_instance_value_for_model(self)->dict:
        suffix = os.path.splitext(self._uri)[1]
        pid = str(ThreeDSIMBase.mongodb_client.getObjectId())
        object_name = "public/pointcloud/" + pid  + suffix
        ThreeDSIMBase.minio_client.upload_file(file_name=self._uri, object_name=object_name)
        return {
            "instance": {
                "filePath": object_name,
                "fileType": suffix # the type of model file, i.e., file suffix
            }
        }
    
