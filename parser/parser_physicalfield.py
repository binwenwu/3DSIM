import os
from pathlib import Path
from typing import Optional, Tuple
from netCDF4 import Dataset
import numpy as np
import math

from base.bounding_volume import BoundingVolume
from base.type import PhysicalFieldType

from base.base_3dsim import ThreeDSIMBase
from rmdb_operations.sql_commonds import *
from mongodb_operations.mongo_template import template_model_asset_physicalfield
from mongodb_operations.mongodb import MongoDB

from tools.utils import generate_short_hash
from minio_operations.minio import get_endpoint_minio

# Notice:
# NetCDF is very flexible, making it difficult to form a standardized ingestion script. 
# Adjustments need to be made for different data types
class ParserPhysicalField(ThreeDSIMBase):
    def __init__(self)-> None:
        super().__init__()
        self._createTime = ''
        self._validTime = []
        self._mimeType = '' 
        self._uri = ''

    # parse a3d physical field asset instance file and insert it into 3dsim
    def add_data(self, mimeType: str,  path:str, 
                 createTime: str='', validTime: list[str]=['',''])->None:
        self._createTime = createTime
        self._validTime = validTime
        self._mimeType = mimeType
        self._uri = path

        print("## the physical field inserting ...")
        self._convert_physicalField_to_fact()
        print("## the physical field inserted")
    
    def _convert_physicalField_to_fact(self)->None:
        physicalFieldAsset  = template_model_asset_physicalfield.copy() 

        if self._mimeType == PhysicalFieldType.NETCDF.value:
            self._read_netcdf(physicalFieldAsset)
        else:
            raise ValueError("the physical field type is not supported currently")
         
        identifier = self._compute_identifier_value()
        physicalFieldAsset.update(identifier)
        self._compute_dimension_value(physicalFieldAsset)
        self._compute_attributes_value(physicalFieldAsset)
        
        ThreeDSIMBase.mongodb_client.add_document("3DModelFact",physicalFieldAsset)
        print(physicalFieldAsset)
        pass

    def _read_netcdf(self, asset: dict)->None:
        nc_dataset = Dataset(self._uri, 'r')
        print("\nnc版本:")
        print(nc_dataset.data_model)
        print("\nnc文件中包含的变量:")
        print(nc_dataset.variables.keys())
        print("\nnc文件中包含的属性:")
        print(nc_dataset.ncattrs())

        epsg = int(4326)
        lon = nc_dataset['lon'][:]
        lat = nc_dataset['lat'][:]
        xmin, xmax = np.min(lon).item(), np.max(lon).item()
        ymin, ymax = np.min(lat).item(), np.max(lat).item()
        resolution_x, resolution_y = abs(float(lon[1]-lon[0])), abs(float(lat[1]-lat[0]))


        zmin = np.mix(nc_dataset['level'][:]).item()
        zmax = np.max(nc_dataset['level'][:]).item()

        # 关闭文件
        nc_dataset.close()        

        print("\nepsg: ",epsg)
        print("\nresolution_x: ",resolution_x)
        print("\nresolution_y: ",resolution_y)

        # convert bounds and max/min value to standard AABB
        bv = BoundingVolume.conver_to_standardAABB(xmin, ymin, xmax, ymax, zmin, zmax)
        resolution_str = f"{resolution_x:.3f},{resolution_y:.3f}"
        res = {"resolution":resolution_str}
        thickness = {"pixelThinkness":zmax - zmin}
        asset.update(res)
        asset.update(bv)
        asset.update(thickness)
    
    # compute the identifier atrribute of the tile
    def _compute_identifier_value(self)->dict:
        return {
            "_id": ThreeDSIMBase.mongodb_client.getObjectId()
        }   

    # compute all of the dimension value of the tile
    def _compute_dimension_value(self, asset: dict)->None:
        spatialDV = self._compute_sptail_dimension_value(asset["boundingVolume"])# get the spatial dimension value
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
    def _compute_sptail_dimension_value(self, aabb: dict) -> dict:
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
        product_type = 'PhysicalField'
        query = "SELECT \"productClass\" FROM public.\"ProductDimension\" WHERE \"productType\" = %s;"
        result = ThreeDSIMBase.postgres.execute_sql_with_return_one(query, (product_type,))
        if result:
            return {
                "productDimension": result
            }
        else:
            raise Exception("Product class not found for product type: 3DTiles")
    
    # compute time dimension value
    def _compute_time_dimension_value(self) -> dict:
        time = ''
        if self._createTime:
            time = self._createTime
        return {"timeDimension": time}
    
    # compute feature dimension value
    def _compute_feature_dimension_value(self) -> dict:
        feature = 'PhysicalField'
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

    # compute the atrributes of the physicalField
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
        object_name = "public/physicalfield/" + pid  + suffix
        ThreeDSIMBase.minio_client.upload_file(file_name=self._uri, object_name=object_name)
        return {
            "instance": {
                "filePath": object_name,
                "fileType": suffix # the type of model file, i.e., file suffix
            }
        }