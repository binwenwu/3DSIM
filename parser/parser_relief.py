import os
from pathlib import Path
from typing import Optional, Tuple
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
import math

from .base.bounding_volume import BoundingVolume
from .base.Transform import Transform
from .base.type import ModelAsset, ReliefType
from tools.render_range_convert import RangeMode, RangeConverter

from base.base_3dsim import ThreeDSIMBase
from rmdb_operations.sql_commonds import *
from mongodb_operations.mongo_template import template_model_asset_relief
from mongodb_operations.mongodb import MongoDB

from tools.utils import generate_short_hash
from minio_operations.minio import get_endpoint_minio
from osgeo import gdal


def reproject_tif(src_path, dst_path, dst_crs='EPSG:4326'):
    with rasterio.open(src_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(dst_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest
                )



# In EPSG 4378, the radius of the Earth is typically defined as the standard Earth radius, which is approximately 6378137 meters
EATEH_RADIUS_EPSG4378 = 6378137

class ParserRelief(ThreeDSIMBase):
    def __init__(self)-> None:
        super().__init__()
        self._createTime = ''
        self._validTime = []
        self._mimeType = '' 
        self._uri = ''

    # parse a 3d relief asset instance file and insert it into 3dsim
    def add_data(self, mimeType: str,  path:str, 
                 createTime: str='', validTime: list[str]=['',''])->None:
        self._createTime = createTime
        self._validTime = validTime
        self._mimeType = mimeType
        self._uri = path

        print("## the relief inserting ...")
        self._convert_relief_to_fact()
        print("## the relief inserted")
    
    def _convert_relief_to_fact(self)->None:
        reliefAsset  = template_model_asset_relief.copy()

        if self._mimeType == ReliefType.GEOTIFF.value:
            self._read_geotiff(reliefAsset)
        else:
            raise ValueError("the relief type is not supported currently")
        
        identifier = self._compute_identifier_value()
        reliefAsset.update(identifier)
        self._compute_dimension_value(reliefAsset)
        self._compute_attributes_value(reliefAsset)
        
        ThreeDSIMBase.mongodb_client.add_document("3DModelFact",reliefAsset)
        print("reliefAsset",reliefAsset)


    def _read_geotiff(self, asset: dict)->None:
        with rasterio.open(self._uri) as src:
            
            epsg = src.crs.to_epsg()
            # unit: degree
            resolution_x = src.res[0] 
            resolution_y = src.res[1]
            bounds = src.bounds
            
            if epsg == 4326:
                # degree to meter
                resolution_x = resolution_x * math.pi * EATEH_RADIUS_EPSG4378 / 180
                resolution_y = resolution_y * math.pi * EATEH_RADIUS_EPSG4378 / 180
            else:
                print("the epsg is not supported currently, they need to be converted into 4326, next")
                raise ValueError("the epsg is not supported currently")
                
            band_data = src.read(1)  # read pixels
            max_value = np.max(band_data) # for max altitude and min altitude
            min_value = np.min(band_data)

            print("max altitude:", max_value)
            print("min altitude:", min_value)
            print("EGSP: ", epsg)
            print("resolution_x: ",resolution_x)
            print("resolution_y: ",resolution_y)
            print("bounds: ",bounds)

            # convert bounds and max/min value to standard AABB
            bv = BoundingVolume.convert_to_standardAABB(bounds.left, bounds.bottom, 
                                              bounds.right, bounds.top, min_value, max_value)
            resolution_str = f"{resolution_x:.3f},{resolution_y:.3f}"
            res = {"resolution":resolution_str}
            asset.update(res)
            asset.update(bv)
    
    # compute the identifier atrribute of the relief
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
        product_type = 'RasterRelief'
        query = "SELECT \"productClass\" FROM public.\"ProductDimension\" WHERE \"productType\" = %s;"
        result = ThreeDSIMBase.postgres.execute_sql_with_return_one(query, (product_type,))
        if result:
            return {
                "productDimension": result
            }
        else:
            raise Exception("Product class not found for product type: RasterRelief")
    
    # compute time dimension value
    def _compute_time_dimension_value(self) -> dict:
        time = ''
        if self._createTime:
            time = self._createTime
        return {"timeDimension": time}
    
    # compute feature dimension value
    def _compute_feature_dimension_value(self) -> dict:
        feature = 'Relief'
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

    # compute the atrributes of the relief
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
        object_name = "public/relief/" + pid  + suffix
        ThreeDSIMBase.minio_client.upload_file(file_name=self._uri, object_name=object_name)
        return {
            "instance": {
                "filePath": object_name,
                "fileType": suffix # the type of model file, i.e., file suffix
            }
        }