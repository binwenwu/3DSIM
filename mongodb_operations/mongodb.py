from pymongo import MongoClient
from bson.objectid import ObjectId


class MongoDB:
    def __init__(self, database="3dsim", host="127.0.0.1", port=27017, username="", password=""):
        self._database = database
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._client = None
        # @author:wbw
        # `_db` 是 `MongoDB` 类的一个属性，用于存储连接到的 MongoDB 数据库的引用。
        self._db = None
        self.connect()

    def __del__(self):
        self.close_connection()

    def connect(self):
        if not self._client:
            try:
                self._client = MongoClient(self._host, self._port, username=self._username, password=self._password)
                if self._database not in self._client.list_database_names():
                    self.createDB()                                            
                else:
                    self._db = self._client[self._database]
                print("MongoDB available!")
            except Exception as e:
                print("Failed to connect to MongoDB:", str(e))
                raise(Exception(e))

    def close_connection(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

    def add_document(self, collection_name, document):
        try:
            collection = self._db[collection_name]
            collection.insert_one(document)
        except Exception as e:
            print("Failed to add document:", str(e))

    def remove_document(self, collection_name, filter):
        try:
            collection = self._db[collection_name]
            collection.delete_one(filter)
        except Exception as e:
            print("Failed to remove document:", str(e))

    def search_documents(self, collection_name, filter):
        try:
            collection = self._db[collection_name]
            documents = collection.find(filter)
            return list(documents)
        except Exception as e:
            print("Failed to search documents:", str(e))
            return []
        
    def createDB(self):
        self._db = self._client[self._database]
        print(f"MongoDB Database '{self._database}' created successfully!")
        
        # create 3DSceneFact collection
        collection = self._db["3DSceneFact"] 
        collection.create_index("_id")
        collection.create_index("spatialDimension")
        collection.create_index("productDimension")
        collection.create_index("viewpointDimension")
        collection.create_index("featureDimension")
        collection.create_index("timeDimension")
        
        # create 3DModelFact collection
        collection = self._db["3DModelFact"]
        collection.create_index("_id")
        collection.create_index("spatialDimension")
        collection.create_index("productDimension")
        collection.create_index("viewpointDimension")
        collection.create_index("featureDimension")
        collection.create_index("timeDimension")

        # create SceneEdge collection 
        collection = self._db["SceneEdge"]
        collection.create_index("fromID")
    
    def getObjectId(self):
        return ObjectId()