from pymongo import MongoClient


# Create MongoDB connection
client = MongoClient(
    host="10.211.55.6",
    port=27017,
    username="admin",
    password="wbw876653771@@"
)

# Get Database
db = client["3dsim"]


collection_names = db.list_collection_names()


total_documents = 0
#Count the number of documents in each collection
for collection_name in collection_names:
    collection = db[collection_name]
    document_count = collection.estimated_document_count()
    print(f'Collection: {collection_name}, 文档数量: {document_count}')
    total_documents += document_count

print(f'所有collection中的文档总数: {total_documents}')
client.close()
