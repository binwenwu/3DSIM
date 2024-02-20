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