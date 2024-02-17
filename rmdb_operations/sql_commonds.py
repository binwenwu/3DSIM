

# create table: SpatialDimension
sql_SpatialDimension = """
CREATE TABLE IF NOT EXISTS public."SpatialDimension"
(
    "ID" serial NOT NULL,
    "gridCode" character varying(255) COLLATE pg_catalog."default",
    "gridExtent" geometry(Polygon, 4326),
    "addressCode" character varying(255) COLLATE pg_catalog."default",
    "addressName" character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT "SpatialDimension_pkey" PRIMARY KEY ("ID")
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."SpatialDimension"
    OWNER to postgres;
"""

# Create index on "gridExtent" column
sql_create_index_gridExtent = """
CREATE INDEX IF NOT EXISTS idx_SpatialDimension_gridExtent
ON public."SpatialDimension" USING GIST ("gridExtent");
"""

# create table: TimeDimension
sql_TimeDimension = """
CREATE TABLE IF NOT EXISTS public."TimeDimension"
(
    "ID" serial NOT NULL,
    "timeCode" character varying COLLATE pg_catalog."default",
    year integer,
    month integer,
    day integer,
    CONSTRAINT "TimeDimension_pkey" PRIMARY KEY ("ID")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."TimeDimension"
    OWNER to postgres;"""

# Create index on "year" column
sql_create_index_year = """
CREATE INDEX IF NOT EXISTS idx_TimeDimension_year
ON public."TimeDimension" ("year");
"""

# Create index on "month" column
sql_create_index_month = """
CREATE INDEX IF NOT EXISTS idx_TimeDimension_month
ON public."TimeDimension" ("month");
"""

# Create index on "day" column
sql_create_index_day = """
CREATE INDEX IF NOT EXISTS idx_TimeDimension_day
ON public."TimeDimension" ("day");
"""

# create table: ProductDimension
sql_ProductDimension = """
CREATE TABLE IF NOT EXISTS public."ProductDimension"
(
    "ID" serial NOT NULL,
    "productClass" character varying(255) COLLATE pg_catalog."default",
    "productType" character varying(255) COLLATE pg_catalog."default",
    "CRS" character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT "ProductDimension_pkey" PRIMARY KEY ("ID")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."ProductDimension"
    OWNER to postgres;"""


# create table: FeatureDimension
sql_FeatureDimension = """
CREATE TABLE IF NOT EXISTS public."FeatureDimension"
(
    "ID" serial NOT NULL,
    "FeatureClass" character varying(255) COLLATE pg_catalog."default",
    "FeatureName" character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT "FeatureDimension_pkey" PRIMARY KEY ("ID")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."FeatureDimension"
    OWNER to postgres;"""


# create table: ViewpointDimension
sql_ViewpointDimension = """
CREATE TABLE IF NOT EXISTS public."ViewpointDimension"
(
    "ID" serial NOT NULL,
    "viewPointLevel" numeric,
    "renderingRangeFrom" numeric,
    "renderingRangeTo" numeric,
    CONSTRAINT "ViewpointDimension_pkey" PRIMARY KEY ("ID")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."ViewpointDimension"
    OWNER to postgres;"""

# insert into table: SpatialDimension
sql_insertSpatialDimension = """insert into "SpatialDimension"("gridCode", "gridExtent", "addressCode", "addressName")values(%s, %s, %s, %s) returning "ID" """


# insert into table: TimeDimension
sql_insertTimeDimension = """insert into "TimeDimension"("timeCode", "year", "month", "day")values(%s, %s, %s,%s) returning "ID" """


# insert into table: ProductionDimension
sql_insertProductionDimension = """insert into "ProductionDimension"("productClass", "productType", "CRS")values(%s, %s, %s) returning"ID" """


# insert into FeatureDimension
sql_insertFeatureDimension = """insert into "FeatureDimension"("featureClass", "featureName")values(%s, %s) returning "ID" """


# insert into ViewpointDimension
sql_insertViewpointDimension = """insert into "ViewpointDimension"("viewPointLevel", "renderingRangeFrom", "renderingRangeTo")values(%s, %s, %s) returning "ID" """


# insert into RootSceneAssetFact
sql_insertRootSceneAssetFact = """insert into "RootSceneAssetFact"("spatialDimension", "timeDimension", "productDimension", "featureDimension", "viewpointDimension", "name", "identifier", "geometricError", "refine", "boundingVolume", "boundingVolumeType", "transform",
"creationDate", "validFrom", "validTo",  "adeOfMetadata", "renderStyle", "leafNodes", "groupNodes")values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning "assetID" """


# insert into SubSceneAssetFact
sql_insertSubSceneAssetFact = """insert into "SubSceneAssetFact"("spatialDimension", "timeDimension", "productDimension", "featureDimension", "viewpointDimension", "name", "identifier", "geometricError", "refine", "boundingVolume", "boundingVolumeType", "transform",
"creationDate", "validFrom", "validTo",  "adeOfMetadata", "renderStyle", "leafNodes", "groupNodes")values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning "assetID" """


# insert into ModelAssetFact
sql_insertModelAssetFact = """insert into "ModelAssetFact"("spatialDimension", "timeDimension", "productDimension", "featureDimension", "viewpointDimension",
"name", "identifier", "boundingVolume", "boundingVolumeType", "transform", "creationDate", "validFrom", "validTo",  "adeOfMetadata", "renderStyle", "modelType", "filePath")values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning "assetID" """


# insert into Scene2SceneEdgeFact
sql_insertScene2SceneEdgeFact = """insert into "Scene2SceneEdgeFact"("fromScene", "toScene", "type")values(%s, %s, %s)"""

# insert into Scene2ModelEdgeFact
sql_insertScene2ModelEdgeFact = """insert into "Scene2ModelEdgeFact"("fromScene", "toModel", "type")values(%s, %s, %s)"""


# get the rootTile by spatial
sql_getRootTileBySpatial = """
SELECT "RootSceneAssetFact"."assetID", "RootSceneAssetFact"."geometricError", "RootSceneAssetFact".refine, "RootSceneAssetFact"."boundingVolume", "RootSceneAssetFact"."boundingVolumeType", "RootSceneAssetFact"."transform", "RootSceneAssetFact"."adeOfMetadata"
FROM "RootSceneAssetFact","SpatialDimension"
WHERE "RootSceneAssetFact"."spatialDimension" = "SpatialDimension"."ID" AND "SpatialDimension"."gridCode" = %s
"""

# get the rootTile by spatial
sql_getRootTileByTime = """
SELECT "RootSceneAssetFact"."assetID", "RootSceneAssetFact"."geometricError", "RootSceneAssetFact".refine, "RootSceneAssetFact"."boundingVolume", "RootSceneAssetFact"."boundingVolumeType", "RootSceneAssetFact"."transform", "RootSceneAssetFact"."adeOfMetadata"
FROM "RootSceneAssetFact","TimeDimension"
WHERE "RootSceneAssetFact"."timeDimension" = "TimeDimension"."ID" AND "TimeDimension"."timeCode" = %s
"""

# get the rootTile by product
sql_getRootTileByProduct = """
SELECT "RootSceneAssetFact"."assetID", "RootSceneAssetFact"."geometricError", "RootSceneAssetFact".refine, "RootSceneAssetFact"."boundingVolume", "RootSceneAssetFact"."boundingVolumeType", "RootSceneAssetFact"."transform", "RootSceneAssetFact"."adeOfMetadata"
FROM "RootSceneAssetFact","ProductionDimension"
WHERE "RootSceneAssetFact"."productDimension" = "ProductionDimension"."ID" AND "ProductionDimension"."productClass" = %s
"""


# get the rootTile by feature
sql_getRootTileByFeature = """
SELECT "RootSceneAssetFact"."assetID", "RootSceneAssetFact"."geometricError", "RootSceneAssetFact".refine, "RootSceneAssetFact"."boundingVolume", "RootSceneAssetFact"."boundingVolumeType", "RootSceneAssetFact"."transform", "RootSceneAssetFact"."adeOfMetadata"
FROM "RootSceneAssetFact","FeatureDimension"
WHERE "RootSceneAssetFact"."featureDimension" = "FeatureDimension"."ID" AND "featureDimension"."featureClass" = %s
"""

# get the rootTile by viewPoint
sql_getRootTileByViewpoint = """
SELECT "RootSceneAssetFact"."assetID", "RootSceneAssetFact"."geometricError", "RootSceneAssetFact".refine, "RootSceneAssetFact"."boundingVolume", "RootSceneAssetFact"."boundingVolumeType", "RootSceneAssetFact"."transform", "RootSceneAssetFact"."adeOfMetadata"
FROM "RootSceneAssetFact","ViewpointDimension"
WHERE "RootSceneAssetFact"."viewpointDimension" = "ViewpointDimension"."ID" AND "ViewpointDimension"."viewPointLevel" = %s
"""


# get tile by rootID
sql_getTileByRootID = """
SELECT "SubSceneAssetFact"."assetID", "SubSceneAssetFact"."geometricError", "SubSceneAssetFact".refine, "SubSceneAssetFact"."boundingVolume", "SubSceneAssetFact"."boundingVolumeType", "SubSceneAssetFact"."transform", "SubSceneAssetFact"."adeOfMetadata", "Scene2SceneEdgeFact".type
FROM "SubSceneAssetFact","Scene2SceneEdgeFact"
WHERE "Scene2SceneEdgeFact"."fromScene" = %s AND "Scene2SceneEdgeFact"."toScene" = "SubSceneAssetFact"."assetID"
"""

# get the tile by spatial
sql_getTileBySpatial = """
SELECT "SubSceneAssetFact"."assetID", "SubSceneAssetFact"."geometricError", "SubSceneAssetFact".refine, "SubSceneAssetFact"."boundingVolume", "SubSceneAssetFact"."boundingVolumeType", "SubSceneAssetFact"."transform", "SubSceneAssetFact"."adeOfMetadata"
FROM "SubSceneAssetFact","SpatialDimension"
WHERE "SubSceneAssetFact"."spatialDimension" = "SpatialDimension"."ID" AND "SpatialDimension"."gridCode" = %s
"""

# get the tile by time
sql_getTileByTime = """
SELECT "SubSceneAssetFact"."assetID", "SubSceneAssetFact"."geometricError", "SubSceneAssetFact".refine, "SubSceneAssetFact"."boundingVolume", "SubSceneAssetFact"."boundingVolumeType", "SubSceneAssetFact"."transform", "SubSceneAssetFact"."adeOfMetadata"
FROM "SubSceneAssetFact","TimeDimension"
WHERE "SubSceneAssetFact"."timeDimension" = "TimeDimension"."ID" AND "TimeDimension"."timeCode" = %s
"""

# get the tile by Product
sql_getTileByProduct = """
SELECT "SubSceneAssetFact"."assetID", "SubSceneAssetFact"."geometricError", "SubSceneAssetFact".refine, "SubSceneAssetFact"."boundingVolume", "SubSceneAssetFact"."boundingVolumeType", "SubSceneAssetFact"."transform", "SubSceneAssetFact"."adeOfMetadata"
FROM "SubSceneAssetFact","ProductionDimension"
WHERE "SubSceneAssetFact"."productDimension" = "ProductionDimension"."ID" AND "ProductionDimension"."productClass" = %s
"""

# get the tile by feature
sql_getTileByFeature = """
SELECT "SubSceneAssetFact"."assetID", "SubSceneAssetFact"."geometricError", "SubSceneAssetFact".refine, "SubSceneAssetFact"."boundingVolume", "SubSceneAssetFact"."boundingVolumeType", "SubSceneAssetFact"."transform", "SubSceneAssetFact"."adeOfMetadata"
FROM "SubSceneAssetFact","FeatureDimension"
WHERE "SubSceneAssetFact"."featureDimension" = "FeatureDimension"."ID" AND "FeatureDimension"."featureClass" = %s
"""

# get the tile by viewpoint
sql_getTileByViewpoint = """
SELECT "SubSceneAssetFact"."assetID", "SubSceneAssetFact"."geometricError", "SubSceneAssetFact".refine, "SubSceneAssetFact"."boundingVolume", "SubSceneAssetFact"."boundingVolumeType", "SubSceneAssetFact"."transform", "SubSceneAssetFact"."adeOfMetadata"
FROM "SubSceneAssetFact","ViewpointDimension"
WHERE "SubSceneAssetFact"."viewpointDimension" = "ViewpointDimension"."ID" AND "ViewpointDimension"."viewPointLevel" = %s
"""

# get content
sql_getContent = """
SELECT "ModelAssetFact"."boundingVolumeType", "ModelAssetFact"."boundingVolume","ModelAssetFact"."transform", "ModelAssetFact"."filePath", "ModelAssetFact"."adeOfMetadata"
FROM "ModelAssetFact", "Scene2ModelEdgeFact"
WHERE "Scene2ModelEdgeFact"."fromScene" = %s AND "Scene2ModelEdgeFact"."toModel" = "ModelAssetFact"."assetID"
"""