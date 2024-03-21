import os
from minio import Minio
from minio.error import S3Error

from minio import Minio
from minio.error import S3Error
import yaml


def get_endpoint_minio() -> str:
    config_file = os.path.join(os.getcwd(), "config/config.yaml")
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    # minio connect params
    minio_config = config.get("minio")
    if minio_config:
        minio_endpoint = minio_config.get("endpoint")
        return 'http://' + minio_endpoint+'/'
    
class MinioClient:
    def __init__(self, endpoint, access_key, secret_key, secure=True):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.minio_client = None
        self.bucket_name = '3dsim'
        self.prefix = 'public/'
        self.connect()

    def __del__(self):
        self.close_connection()

    def connect(self):
        try:
            print()
            self.minio_client = Minio(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            prefix = "public/"
            policy = '{"Version":"2012-10-17","Statement":[{"Action":["s3:GetObject"],"Effect":"Allow","Principal":"*","Resource":["arn:aws:s3:::' + self.bucket_name + '/' + prefix + '*"],"Sid":""}]}'
            self.minio_client.set_bucket_policy(self.bucket_name, policy)
            print("Connected to MinIO successfully!")
            print("MinIO available!")
        except S3Error as e:
            print("Error to connect the MinIO:", e)

    def close_connection(self):
        if self.minio_client:
            self.minio_client = None
            print("Connection to MinIO closed.")

    def upload_file(self, file_name, object_name =None):
        try:
            if not self.minio_client:
                raise ValueError("Not connected to MinIO.")
            
            file_name = os.path.abspath(file_name)
            if not object_name:
                object_name = file_name

            with open(file_name, 'rb') as file_data:
                self.minio_client.put_object(
                    self.bucket_name,
                    object_name,
                    file_data,
                    length=os.path.getsize(file_name) # 获取需要上传文件的大小（字节）
                )
            print(f"File '{object_name}' uploaded to '{self.bucket_name}'")
        except S3Error as e:
            print("Error:", e)
    
    
    def upload_folder(self, folder_path, prefix=None):
        try:
            if not self.minio_client:
                raise ValueError("Not connected to MinIO.")
            
            folder_path = os.path.abspath(folder_path)
            for root, dirs, files in os.walk(folder_path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    if prefix:
                        object_name = os.path.join(prefix, os.path.relpath(file_path, folder_path))
                    else:
                        object_name = os.path.relpath(file_path, folder_path)
                    self.upload_file(file_path, object_name)
                    
            print(f"Folder '{folder_path}' uploaded to '{self.bucket_name}'")
        except S3Error as e:
            print("Error:", e)


