import os
import yaml
from abc import ABC, abstractmethod
from rmdb_operations.postgres import PostgreSQL
from mongodb_operations.mongodb import MongoDB
from minio_operations.minio import MinioClient
from rmdb_operations.initialize_dimension_tables import DimTableInitializer

class ThreeDSIMBase(ABC):
    postgres = None
    mongodb_client = None
    minio_client = None

    def __init__(self, config_file: str = None):
        if config_file is None:
            config_file = os.path.join(os.getcwd(), "config.yaml")
        self._connect_databases(config_file)

    def _connect_databases(self, config_file: str):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)

        # postgresql connect params
        database_config = config["postgresql"]
        pg_database = database_config.get("database")
        pg_user = database_config.get("user")
        pg_password = database_config.get("password")
        pg_host = database_config.get("host")
        pg_port = database_config.get("port")
        self._connect_postgresql(pg_database, pg_user, pg_password, pg_host, pg_port)

        # mongodb connect params
        mongodb_config = config["mongodb"]
        mongodb_database = mongodb_config.get("database")
        mongodb_host = mongodb_config.get("host")
        mongodb_port = mongodb_config.get("port")
        mongodb_username = mongodb_config.get("username")
        mongodb_password = mongodb_config.get("password")
        self._connect_mongodb(mongodb_database, mongodb_host, mongodb_port, mongodb_username, mongodb_password)

        # minio connect params
        minio_config = config.get("minio")
        if minio_config:
            minio_endpoint = minio_config.get("endpoint")
            minio_access_key = minio_config.get("access_key")
            minio_secret_key = minio_config.get("secret_key")
            self._connect_minio(minio_endpoint, minio_access_key, minio_secret_key)

    def _connect_postgresql(self, database: str = None, user: str = "postgres", password: str = None,
                           host: str = "127.0.0.1", port: str = "5432") -> None:
        if ThreeDSIMBase.postgres is None:
             # @auther:wbw 
             # 先获取连接，再初始化维度表
            ThreeDSIMBase.postgres = PostgreSQL(database=database, user=user, password=password, host=host, port=port)
            initializer = DimTableInitializer(ThreeDSIMBase.postgres)  # initialize all dimension tables
            initializer.do_initialize()

    def _connect_mongodb(self, database: str = None, host: str = "localhost", port: int = 27017,
                        username: str = '', password: str = '') -> None:
        if ThreeDSIMBase.mongodb_client is None:
            ThreeDSIMBase.mongodb_client = MongoDB(database=database, host=host, port=port, username=username, password=password)

    def _connect_minio(self, endpoint: str, access_key: str, secret_key: str):
        if ThreeDSIMBase.minio_client is None:
            ThreeDSIMBase.minio_client = MinioClient(endpoint, access_key=access_key, secret_key=secret_key, secure=False)
