"""
该资产在MongoDB中的一条记录的例子, 其他类似:
"id": "1",
"spatialDimension": [106_130],
"timeDimension": [20230106],
"productDimension": "1",
"featureDimension": "230000",
"viewpointDimension": [1],
"genericName": "3dsim_Building",
"boundingVolume": {"type":"AABB", "bv": [-73.9612660018684,40.6707788088504,0,-73.7000626459572,40.7902961004823,205.564101845492]},
"transformToWorld": [],
"creationDate": "20230106",
"validTimeSpan": ['19000101','29991212'],
"adeOfMetadata": {"asset":{"version":"1.0","extras":{"ion":{"georeferenced":"true","movable":"true","renderable":"true","shadowCasting":"true","shadowReceiving":"true","transformable":"true","visible":"false"}}}},
"renderStyle": ""
"""


template_scene_asset = {
    "_id": "", # identifier
    "spatialDimension": [],
    "timeDimension": [],
    "productDimension": "",
    "featureDimension": "",
    "viewpointDimension": [],
    "genericName": "",
    "boundingVolume": {
        "type": "",
        "bv": []
    },
    "transformToWorld": [], # 16 flost for Matrix 4*4
    "creationDate": "",
    "validTimeSpan": ['19000101','29991212'],
    "adeOfMetadata": {},
    "renderStyle": ""
}


template_model_asset = {
    "_id": "",  # identifier
    "spatialDimension": [],
    "timeDimension": [],
    "productDimension": "",
    "featureDimension": "",
    "viewpointDimension": [],
    "genericName": "",
    "boundingVolume": {
        "type": "",
        "bv": []
    },
    "transformToWorld": [], # 16 flost for Matrix 4*4
    "creationDate": "",
    "validTimeSpan": ['19000101','29991212'],
    "adeOfMetadata": {},
    "instance": {
        "filePath": "", # the path of model file
        "fileType": "" # the type of model file, i.e., file suffixe
    }
}


template_model_asset_relief = {
    "_id": "",  # identifier
    "spatialDimension": [],
    "timeDimension": [],
    "productDimension": "",
    "featureDimension": "",
    "viewpointDimension": [],
    "genericName": "",
    "boundingVolume": {
        "type": "",
        "bv": []
    },
    "transformToWorld": [], # 16 flost for Matrix 4*4
    "creationDate": "",
    "validTimeSpan": ['19000101','29991212'],
    "adeOfMetadata": {},
    "instance": {
        "filePath": "", # the path of model file
        "fileType": "" # the type of model file, i.e., file suffixe
    },
    "resolution": "", # the resolution of model
    # and another attributes for the model, such as resolution, material, etc.
}

template_model_asset_pointcloud = {
    "_id": "",  # identifier
    "spatialDimension": [],
    "timeDimension": [],
    "productDimension": "",
    "featureDimension": "",
    "viewpointDimension": [],
    "genericName": "",
    "boundingVolume": {
        "type": "",
        "bv": []
    },
    "transformToWorld": [], # 16 flost for Matrix 4*4
    "creationDate": "",
    "validTimeSpan": ['19000101','29991212'],
    "adeOfMetadata": {},
    "instance": {
        "filePath": "", # the path of model file
        "fileType": "" # the type of model file, i.e., file suffixe
    },
    # and another attributes for the model, such as resolution, material, etc.
}

template_model_asset_physicalfield = {
    "_id": "",  # identifier
    "spatialDimension": [],
    "timeDimension": [],
    "productDimension": "",
    "featureDimension": "",
    "viewpointDimension": [],
    "genericName": "",
    "boundingVolume": {
        "type": "",
        "bv": []
    },
    "transformToWorld": [], # 16 flost for Matrix 4*4
    "creationDate": "",
    "validTimeSpan": ['19000101','29991212'],
    "adeOfMetadata": {},
    "instance": {
        "filePath": "", # the path of model file
        "fileType": "" # the type of model file, i.e., file suffixe
    },
    "resolution": "", # the resolution of model
    "pixelThinkness": "",
    # and another attributes for the model, such as resolution, material, etc.
}




template_asset_edge = {
    "fromID": "", # the identier id of father asset
    "toID": "", # the identier id of father asset
    "type": "", # 1:scene 2 scene; 2: scene 2 model
    "transform": [], # For node reference: 16 flost for Matrix 4*4
    "range": {} # for lod render range：{renderRange: "", rangeMode: ""}
}