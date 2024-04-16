import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from data_operations.query import Query


Query = Query()


@csrf_exempt
def query(request):
    if request.method == "POST":
        queryParams = json.loads(request.body)
        feature = queryParams["feature"]
        product = queryParams["product"]
        validFrom = format_date(queryParams["validFrom"])
        validTo = format_date(queryParams["validTo"])
        viewedRange = queryParams["viewedRange"]
        lon = queryParams["lon"]
        lat = queryParams["lat"]
        assetType = queryParams["assetType"]

        assets = []
        if assetType == "3DScene":
            assets = querySceneAsset(
                [product],
                [lon[0], lat[0], lon[1], lat[1]],
                [validFrom, validTo],
                [feature],
                viewedRange,
                isRoot=False,
            )
        elif assetType == "3DModel":
            assets = queryModelAsset(
                [product],
                [lon[0], lat[0], lon[1], lat[1]],
                [validFrom, validTo],
                [feature],
                viewedRange,
            )
        else:
            sceneAssets = querySceneAsset(
                [product],
                [lon[0], lat[0], lon[1], lat[1]],
                [validFrom, validTo],
                [feature],
                viewedRange,
                isRoot=False,
            )
            modelAssets = queryModelAsset(
                [product],
                [lon[0], lat[0], lon[1], lat[1]],
                [validFrom, validTo],
                [feature],
                viewedRange,
            )
            assets = sceneAssets + modelAssets

        return JsonResponse(
            {"message": "Query successfully", "assets": assets}, status=200
        )
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)


def querySceneAsset(
    product: list[str],
    spatialExtent: list[float],
    timeSpan: list[str],
    feature: list[str],
    viewedRange: list[float],
    isRoot: bool,
) -> list:

    assets = []
    results = Query.query_sceneAsset(
        product,
        spatialExtent,
        timeSpan,
        feature,
        viewedRange,
        isRoot,
    )

    for result in results:
        asset = {
            "assetId": result["_id"],
            "assetType": "3DScene",
            "feature": result["featureDimension"],
            "product": result["productDimension"],
            "validTimeSpan": result["validTimeSpan"],
            "creationDate": result["creationDate"],
            "version": "version-1",
            "boundingVolume": result["boundingVolume"]["bv"],
            "genericName": result["genericName"],
        }
        assets.append(asset)
    return assets


def queryModelAsset(
    product: list[str],
    spatialExtent: list[float],
    timeSpan: list[str],
    feature: list[str],
    viewedRange: list[float],
) -> list:

    assets = []
    results = Query.query_modelAsset(
        product,
        spatialExtent,
        timeSpan,
        feature,
        viewedRange,
    )

    for result in results:
        asset = {
            "assetId": result["_id"],
            "assetType": "3DModel",
            "feature": result["featureDimension"],
            "product": result["productDimension"],
            "validTimeSpan": result["validTimeSpan"],
            "creationDate": result["creationDate"],
            "version": "version-1",
            "boundingVolume": result["boundingVolume"]["bv"],
            "genericName": result["genericName"],
            "filePath": result["instance"]["filePath"],
        }
        assets.append(asset)
    return assets



# Format the date to the format of yyyymmdd
def format_date(date_array):
    year = str(date_array[0])
    month = str(date_array[1]).zfill(2)
    day = str(date_array[2]).zfill(2)
    return year + month + day
