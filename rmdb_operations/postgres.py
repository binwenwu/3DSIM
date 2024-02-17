import psycopg2
from psycopg2 import pool
from psycopg2.extensions import *

'''
这是一个名为`PostgreSQL`的Python类,用于管理PostgreSQL数据库的连接和操作。以下是每个方法的功能:
- `__init__`：初始化方法，设置数据库连接参数，并尝试创建数据库和测试连接。
- `__del__`：析构方法，关闭所有数据库连接。
- `get_connection`：获取数据库连接，如果连接池不存在，则创建一个新的连接池。
- `close_connection`：关闭所有数据库连接。
- `execute_sql`: 执行没有返回结果的SQL语句。
- `execute_sql_with_return_all`:执行SQL语句并返回所有结果。
- `execute_sql_with_return_one`: 执行SQL语句并返回第一个结果。
- `check_table_exists`：检查指定的表是否存在。
- `execute_batch_sql`: 批量执行SQL语句。
- `create_database`: 创建数据库, 并尝试启用PostGIS扩展。
- `test_connection`：测试数据库连接是否成功。

这个类使用了`psycopg2`库来操作PostgreSQL数据库, `psycopg2`是Python中最常用的PostgreSQL数据库操作库。
'''
class PostgreSQL:
    def __init__(self, database="3dsim", user="postgres", password=None, host="127.0.0.1", port="5432", max_connections=200):
        self._database = database
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._max_connections = max_connections
        self._conn_pool = None
        self._conn = None

        self.create_database()

        if self.test_connection():
            print("Test: PostgreSQL available")
        else:
            print("Failed to connect to PostgreSQL.")

    def __del__(self):
        self.close_connection()

    def get_connection(self):
        if self._conn_pool is None:
            self._conn_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=5,
                maxconn=self._max_connections,
                database=self._database,
                user=self._user,
                password=self._password,
                host=self._host,
                port=self._port
            )
            print("PGSQL Connected")
            print("Connection pool size: ", len(self._conn_pool._pool))
        if self._conn is None:
            self._conn = self._conn_pool.getconn()
            return self._conn
        else:
            return self._conn

    def close_connection(self):
        if self._conn_pool:
            self._conn_pool.closeall()

    def execute_sql(self, sql, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        cursor.close()

    def execute_sql_with_return_all(self, sql, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()

        result = cursor.fetchall()
        cursor.close()
        return result

    def execute_sql_with_return_one(self, sql, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()

        result = cursor.fetchone()
        if result:
            return result[0]
        cursor.close()

    def check_table_exists(self, table_name):
        sql = f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')"
        result = self.execute_sql_with_return_one(sql)
        return result
    
    def execute_batch_sql(self, sql, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            with conn:
                cursor.executemany(sql, data)  
        except (psycopg2.Error, Exception) as e:
            print("Failed to execute batch SQL:", str(e))
        finally:
            conn.commit()  
            cursor.close()

    def create_database(self):
        try:
            # Connect to the default "postgres" database without autocommit
            conn = psycopg2.connect(
                database="postgres",
                user=self._user,
                password=self._password,
                host=self._host,
                port=self._port
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            # Create the target database
            cursor.execute(f'CREATE DATABASE "{self._database}"')
            print(f"Create database '{self._database}' successfully!")  
            cursor.close()
            conn.close()

            self.execute_sql('CREATE EXTENSION IF NOT EXISTS postgis')
            print("PostGIS extension enabled!")

        except psycopg2.Error as e:
            print(f"{e}")
            if conn:
                conn.close()

    def test_connection(self):
        try:
            conn = psycopg2.connect(
                database=self._database,
                user=self._user,
                password=self._password,
                host=self._host,
                port=self._port
            )
            conn.close()
            return True
        except (psycopg2.Error, Exception):
            return False
