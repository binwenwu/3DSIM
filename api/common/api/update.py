import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from data_operations.update import Update



Update = Update()

@csrf_exempt
def update(request):
    if request.method == "POST":
        queryParams = json.loads(request.body)
        if(queryParams["assetType"] == "3DScene"):
            updateSceneAsset(scene_id=queryParams["assetId"], update_data=queryParams["updateData"])
        else:
            updateModelAsset(model_id=queryParams["assetId"], update_data=queryParams["updateData"])

        return JsonResponse(
            {"message": "Query successfully"}, status=200
        )
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)



def updateSceneAsset(scene_id: str, update_data: dict):
    """
    Update root scene assets based on specified criteria.
    :param scene_id: _id of the scene to be updated
    :param update_data: a dictionary containing the fields to be updated and their new values
    """

    if not scene_id:
        raise ValueError("scene_id is required.")

    if not update_data:
        raise ValueError("update_data is required.")

    Update.update_sceneAsset(scene_id = scene_id,update_data=update_data)


    

def updateModelAsset(model_id: str, update_data: dict):
    """
    Update model assets based on specified criteria.
    :param model_id: _id of the model to be updated
    :param update_data: a dictionary containing the fields to be updated and their new values
    """

    if not model_id:
        raise ValueError("model_id is required.")

    if not update_data:
        raise ValueError("update_data is required.")

    Update.update_modelAsset(model_id = model_id,update_data=update_data)
    