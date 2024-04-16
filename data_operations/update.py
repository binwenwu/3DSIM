from datetime import datetime
from bson.objectid import ObjectId
from data_operations.query import Query
from base.base_3dsim import ThreeDSIMBase



class Update(ThreeDSIMBase):

    def __init__(self):
        self.query = Query()

    def update_sceneAsset(self, scene_id, update_data: dict):
        """
        Update root scene assets based on specified criteria.
        :param scene_id: _id of the scene to be updated
        :param update_data: a dictionary containing the fields to be updated and their new values
        """

        if not scene_id:
            raise ValueError("scene_id is required.")

        if not update_data:
            raise ValueError("update_data is required.")

        query = {
            "_id": scene_id
        }

        ThreeDSIMBase.mongodb_client.update_document("3DSceneFact", query, update_data)


    def update_modelAsset(self, model_id: ObjectId, update_data: dict):
        """
        Update model assets based on specified criteria.
        :param model_id: _id of the model to be updated
        :param update_data: a dictionary containing the fields to be updated and their new values
        """

        if not model_id:
            raise ValueError("model_id is required.")

        if not update_data:
            raise ValueError("update_data is required.")

        query = {
            "_id": model_id
        }
        
        ThreeDSIMBase.mongodb_client.update_document("3DModelFact", query, update_data)



    
    
    




    