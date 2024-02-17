from pymongo import MongoClient
from bson.objectid import ObjectId


"""
@author:wbw
这段代码定义了一个名为 `MongoDB` 的 Python 类，用于连接 MongoDB 数据库，并提供了一些方法来操作数据库中的文档。

在类的构造函数中，定义了 `database`、`host`、`port`、`username` 和 `password` 等参数，用于指定数据库的连接信息。
在 `connect` 方法中，使用 `pymongo` 模块的 `MongoClient` 类连接数据库，并检查指定的数据库是否存在，如果不存在，
则调用 `createDB` 方法创建数据库。在 `add_document`、`remove_document` 和 `search_documents` 方法中，
分别实现了向指定集合添加文档、删除指定集合中的文档和查询指定集合中的文档的功能。在 `createDB` 方法中，创建了三个集合，
分别为 `3DSceneFact`、`3DModelFact` 和 `SceneEdge`，并为每个集合创建了多个索引。在 `getObjectId` 方法中，返回了一个新的 `ObjectId` 对象。
"""
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