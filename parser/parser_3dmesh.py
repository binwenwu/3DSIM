import os



from base.base_3dsim import ThreeDSIMBase


class Parser3DMesh(ThreeDSIMBase):
    def __init__(self)-> None:
        pass
    

    # parse a 3d mesh asset instance file and insert it into 3dsim
    def add_data():
        pass

    
    def _convert_mesh_to_fact(self)->None:
        pass


    
    def _read_obj(self, asset: dict)->None:
        pass


    # compute the identifier atrribute of the tile
    def _compute_identifier_value(self)->dict:
        return {
            "_id": ThreeDSIMBase.mongodb_client.getObjectId()
        }   