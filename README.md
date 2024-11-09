# Get Started

## Environment

1. Software dependencies

- Python 3.10+
- PostgreSQL 14.5
- PostGIS
- MinIO
- MongoDB

2. Install python 3rdParty dependencies

```bash
pip install -r requirements.txt
```

> If you have any problem with the above command, you can also install them by

```bash
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

# Catalogue
```text
├── base                         Basic Entity Object
├── data_operations              Data asset operation(CRUD) 
├── minio_operations             Object storage operation
├── mongodb_operations           MongoDB Operations
├── parser                       3D asset parser
├── rmdb_operations              PostgreSQL Operations
├── test.ipynb                   Partial test cases
├── tools                        Conversion tool
```

# Usage

## query 3d asset

1. query model assets

```python
from data_operations.query import Query
query = Query()
result = query.query_modelAsset(
         product = ['RasterRelief','PointCloud','PhysicalField', '3DMesh'], 
         spatialExtent = [-180, -90, 180, 90],
         timeSpan = ['19000101', '20990101'], 
         feature = ['Building'], 
         viewedRange = [0,9999999])
```
2. query 3d root scene assets

```python
from query import Query
query  = Query()
result = query.query_rootSceneAsset(
         product = ['3DTiles','CityGML','OSG', 'I3S'], 
         spatialExtent = [-180, -90, 180, 90],
         timeSpan = ['19000101', '20990101'], 
         feature = ['Building'], 
         viewedRange = [0,9999999],
         isRoot=True)
```
3. query scene assets: 3dtiles

```python
from query import Query
query  = Query()
result = query.query_rootSceneAsset(
         product = ['3DTiles'], 
         spatialExtent = [-180, -90, 180, 90],
         timeSpan = ['19000101', '20990101'], 
         feature = ['Building'], 
         viewedRange = [0,9999999],
         isRoot=True)
p3d = Parser3DTiles()
p3d.save_data_to3dtiles(sceneAsset=results[0], path='./tileset.json',query=query)
```