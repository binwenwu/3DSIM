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
    "pixelThinkness": "", # the pixel thinkness of model
    # and another attributes for the model, such as resolution, material, etc.
}




template_asset_edge = {
    "fromID": "", # the identier id of father asset
    "toID": "", # the identier id of father asset
    "type": "", # 1:scene 2 scene; 2: scene 2 model
    "transform": [], # For node reference: 16 flost for Matrix 4*4
    "range": {} # for lod render range：{renderRange: "", rangeMode: ""}
}