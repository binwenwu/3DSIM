```
.
├── base                                                 Basic Type Definition
│   ├── base_3dsim.py
│   ├── bounding_volume.py 
│   └── type.py
├── config.yaml  										 Configuration file (storage)
├── feature_category.yaml                            
├── product_category.yaml
├── minio_operations                                     Minio operation
│   ├── minio.py
├── mongodb_operations                                   Mongo operation
│   ├── initialize_fact_tables.py
│   ├── __init__.py
│   ├── mogon_counter.py
│   ├── mongodb.py
│   ├── mongo_template.py
├── rmdb_operations                                      PostGIS operation
│   ├── initialize_dimension_tables.py
│   ├── __init__.py
│   ├── postgres.py
│   ├── sql_commonds.py
│   └── tableparams.py
├── parser                                               Various data analysis
│   ├── model_parser.py
│   ├── parser_3dmesh.py
│   ├── parser_3dtiles
│   │   ├── parser_3dtiles.py
│   │   └── tile3d_parser
│   │       ├── __init__.py
│   │       ├── read_3dtiles.py
│   │       └── tileset_parser
│   │           ├── base_extension.py
│   │           ├── base_metadata.py
│   │           ├── bounding_volume_box.py
│   │           ├── bounding_volume.py
│   │           ├── bounding_volume_region.py
│   │           ├── bounding_volume_sphere.py
│   │           ├── content.py
│   │           ├── contents.py
│   │           ├── exceptions.py
│   │           ├── __init__.py
│   │           ├── root_property.py
│   │           ├── tile.py
│   │           ├── tileset.py
│   │           └── type.py
│   ├── parser_physicalfield.py
│   ├── parser_pointcloud.py
│   ├── parser_relief.py
├── requirements.txt                                     Dependency Package
├── tools                                                Instrumental function
│   ├── query.py
│   ├── render_range_convert.py
│   └── utils.py
```

# Get Started

## Environment

1. Software dependencies

- Python3.10+
- PostgreSQL 14.5
- PostGIS
- MinIO
- MongoDB

2. Install python 3rdParty dependencies

```
pip install -r requirements.txt
```

If you have any problem with the above command, you can also install them by

```
pip install numpy
pip install PyYAML

pip install psycopg2
pip install postgis
pip install pymongo
pip install minio

pip install pyproj
pip install mmh3
pip install rasterio
pip install laspy
pip install laspy[lazrs]
pip install netCDF4

```

3. Set download policy to MinIO

# Usage

## query 3d asset

1. query model assets

```
from query import Query
query  = Query()
result = query.query_modelAsset(self, 
         product: list[str]=['RasterRelief','PointCloud','PhysicalField', '3DMesh'], 
         spatialExtent: list[float] = [-180, -90, 180, 90],
         timeSpan: list[str] = ['19000101', '20990101'], 
         feature: list[str] = ['Building'], 
         viewedRange: list[float] = [0,9999999])
```
2. query 3d root scene assets

```
from query import Query
query  = Query()
result = query.query_rootSceneAsset(self, 
         product: list[str]=['3DTiles','CityGML','OSG', 'I3S'], 
         spatialExtent: list[float] = [-180, -90, 180, 90],
         timeSpan: list[str] = ['19000101', '20990101'], 
         feature: list[str] = ['Building'], 
         viewedRange: list[float] = [0,9999999])
```
3. query scene assets: 3dtiles

```
from query import Query
query  = Query()
result = query.query_rootSceneAsset(self, 
         product: list[str]=['3DTiles','CityGML','OSG', 'I3S'], 
         spatialExtent: list[float] = [-180, -90, 180, 90],
         timeSpan: list[str] = ['19000101', '20990101'], 
         feature: list[str] = ['Building'], 
         viewedRange: list[float] = [0,9999999])
p3d = Parser3DTiles()
p3d.save_data_to3dtiles(sceneAsset=result[0], path='./tilese1',query=query)
```                