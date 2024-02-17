from typing import Literal

#*****************************
#   关于各个表格的参数获得
#*****************************

class SpatialTable:
    def __init__(self,
            ID: int | None = None,
            gridCode: str | None = None,
            gridExtent: str | None = None,
            addressCode: str | None = None,
            addressName: str | None = None
        ) -> None:
        self.ID = ID
        self.gridCode = gridCode
        self.gridExtent = gridExtent
        self.addressCode = addressCode
        self.addressName = addressName
    
    def getParams(self):
        return (self.gridCode, self.gridExtent, self.addressCode, self.addressName)


class TimeTable():
    def __init__(self,
        ID: int | None = None,
        timeCode: str | None = None,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
        ) -> None:
        self.ID = ID
        self.timeCode = timeCode
        self.year = year
        self.month = month
        self.day = day
        
    def getParams(self):
        return (self.timeCode, self.year, self.month, self.day)
    

class ProductTable:
    def __init__(self,
                 ID: int | None = None,
                 productClass: str | None = None,
                 productType: str | None = None,
                 CRS: int | None = None
                 ) -> None:
        self.ID = ID
        self.productClass = productClass
        self.productType = productType
        self.CRS = CRS

    def getParams(self):
        return (self.productClass, self.productType, self.CRS)
        

class FeatureTable:
    def __init__(self,
                 ID: int | None = None,
                 featureClass: str | None = None,
                 featureName: str | None = None
                 ) -> None:
        self.ID = ID
        self.featureClass = featureClass
        self.featureName = featureName
    
    def getParams(self):
        return (self.featureClass, self.featureName)
    

class Viewpoint:
    def __init__(self,
                 ID: int | None = None,
                 viewPointLevel: str | None = None,
                 renderingRangeFrom: str | None = None,
                 renderingRangeTo: str | None =None
                 ) -> None:
        self.ID = ID
        self.viewPointLevel = viewPointLevel
        self.renderingRangeFrom = renderingRangeFrom
        self.renderingRangeTo = renderingRangeTo

    def getParams(self):
        return (self.viewPointLevel, self.renderingRangeFrom, self.renderingRangeTo)
    

class Scene:
    def __init__(self,
                 assetID: int | None = None,
                 spatialDimension: int | None = None,
                 timeDimension: int | None = None,
                 productDimension: int | None = None,
                 featureDimension: int | None = None,
                 viewpointDimension: int | None = None,
                 name: str | None = None,
                 identifier: str | None = None,
                 geometricError: float | None = None,
                 refine: Literal["ADD", "REPLACE"] | None = None,
                 boundingVolume: list[float] | None = None,
                 boundingVolumeType: str | None = None,
                 transform: str | None = None,
                 creationDate: str | None = None,
                 validFrom: str | None = None,
                 validTo: str | None = None,
                 adeOfMetadata: str | None = None,
                 renderStyle: str | None = None,
                 leafNodes: str | None = None,
                 groupNodes: str | None = None) -> None:
        self.assetID = assetID
        self.spatialDimension = spatialDimension
        self.timeDimension = timeDimension
        self.productDimension = productDimension
        self.featureDimension = featureDimension
        self.viewpointDimension = viewpointDimension
        self.name = name
        self.identifier = identifier
        self.geometricError = geometricError
        self.refine = refine
        self.boundingVolume = boundingVolume
        self.boundingVolumeType = boundingVolumeType
        self.transform = transform
        self.creationDate = creationDate
        self.validFrom = validFrom
        self.validTo = validTo
        self.adeOfMetdata = adeOfMetadata
        self.renderStyle = renderStyle
        self.leafNodes = leafNodes
        self.groupNodes = groupNodes

    def getParams(self):
        return (self.spatialDimension, self.timeDimension, self.productDimension, self.featureDimension, self.viewpointDimension,self.name, self.identifier, self.geometricError, self.refine,
                self.boundingVolume, self.boundingVolumeType, self.transform, self.creationDate, self.validFrom, self.validTo, self.adeOfMetdata, self.renderStyle, self.leafNodes, self.groupNodes)
    

class RootScene(Scene):
    pass


class SubScene(Scene):
    pass
       
        
class Model(Scene):
    def __init__(self,
                 assetID: int | None = None,
                 spatialDimension: int | None = None,
                 timeDimension: int | None = None,
                 productDimension: int | None = None,
                 featureDimension: int | None = None,
                 viewpointDimension: int | None = None,
                 name: str | None = None,
                 identifier: str | None = None,
                 boundingVolume: list[float] | None = None,
                 boundingVolumeType: str | None = None,
                 transform: str | None = None,
                 creationDate: str | None = None,
                 validFrom: str | None = None,
                 validTo: str | None = None,
                 adeOfMetadata: str | None = None,
                 renderStyle: str | None = None,
                 modelType: str | None = None,
                 filePath: str | None = None) -> None:
        super().__init__(assetID = assetID,
                         spatialDimension = spatialDimension,
                         timeDimension = timeDimension,
                         productDimension = productDimension,
                         featureDimension = featureDimension,
                         viewpointDimension = viewpointDimension,
                         name = name,
                         identifier = identifier,
                         boundingVolume = boundingVolume,
                         boundingVolumeType = boundingVolumeType,
                         transform = transform,
                         creationDate = creationDate,
                         validFrom = validFrom,
                         validTo = validTo,
                         adeOfMetadata = adeOfMetadata,
                         renderStyle = renderStyle)
        self.modelType = modelType
        self.filePath = filePath

    def getParams(self):
        return (self.spatialDimension, self.timeDimension, self.productDimension, self.featureDimension, self.viewpointDimension, self.name, self.identifier,
                self.boundingVolume, self.boundingVolumeType, self.transform, self.creationDate, self.validFrom, self.validTo, self.adeOfMetdata, self.renderStyle, self.modelType, self.filePath)
        

class Edge:
    def __init__(self,
                 edgeID: int | None = None,
                 fromScene: int | None = None,
                 toScene: int | None = None,
                 Type: int | None = None) -> None:
        self.edgeID = edgeID
        self.fromScene = fromScene
        self.toScene = toScene
        self.Type = Type

    def getParams(self):
        return (self.fromScene, self.toScene, self.Type)
    

class Scene2Scene(Edge):
    pass


class Scene2Model(Edge):
    pass
        
