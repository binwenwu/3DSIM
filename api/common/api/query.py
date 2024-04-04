import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from data_operations.query import Query


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
        query = Query()
        if assetType == "3DScene":
            results = query.query_sceneAsset(
                [product],
                [lon[0], lat[0], lon[1], lat[1]],
                [validFrom, validTo],
                [feature],
                viewedRange,
                isRoot=False,
            )
            for result in results:
                asset = {
                    "assetId": result["_id"],
                    "assetType": "3DScene",
                    "feature": result["featureDimension"],
                    "product": result["productDimension"],
                    "validTimeSpan": result["validTimeSpan"],
                    "creationDate": result["creationDate"],
                    "version": "v1",
                    "boundingVolume": result["boundingVolume"]["bv"],
                }
                assets.append(asset)
        elif assetType == "3DModel":
            results = query.query_modelAsset(
                [product],
                [lon[0], lat[0], lon[1], lat[1]],
                [validFrom, validTo],
                [feature],
                viewedRange,
            )
        else:
            pass
        
        
        return JsonResponse({"message": "Query successfully","assets": assets}, status=200)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)


# Format the date to the format of yyyymmdd
def format_date(date_array):
    year = str(date_array[0])
    month = str(date_array[1]).zfill(2)
    day = str(date_array[2]).zfill(2)
    return year + month + day
