from pymongo import MongoClient


# 创建MongoDB连接
client = MongoClient(
    host="10.211.55.6",
    port=27017,
    username="admin",
    password="wbw876653771@@"
)

# 获取数据库
db = client["3dsim"]

# 获取所有collection
collection_names = db.list_collection_names()


total_documents = 0
# 统计每个collection中的文档数量
for collection_name in collection_names:
    collection = db[collection_name]
    document_count = collection.estimated_document_count()  # 或者使用count_documents方法
    print(f'Collection: {collection_name}, 文档数量: {document_count}')
    total_documents += document_count

print(f'所有collection中的文档总数: {total_documents}')
# 关闭数据库连接
client.close()
