import os
import yaml
import time
from datetime import date, timedelta
from .sql_commonds import *

"""
@author:wbw
pg数据库中维度表初始化
"""
class DimTableInitializer:
    def __init__(self, postgresql):
        self.postgresql = postgresql

    # @author:wbw
    # 初始化各个维度表，先创建字段，再创建索引，然后再初始化表内容
    # 1.空间维度表
    # 2.时间维度表
    # 3.特征维度表
    # 4.产品维度表
    # 5.视点维度表
    def do_initialize(self):
        if not self.postgresql.check_table_exists('SpatialDimension'):
            print("## Create spatial dimension tables...")
            # author:wbw
            # 1. 创建空间维度表
            # 2. 建立索引
            self.postgresql.execute_sql(sql_SpatialDimension)
            self.postgresql.execute_sql(sql_create_index_gridExtent)
            print("## Create spatial dimension tables done")
            # Spatial dimension initialization
            # 3. 然后再初始化表内容
            sp_dim = SpatialDimInitializer(self.postgresql)
            print("##### Spatial dimension table initializing ...")
            start_time = time.time()
            sp_dim.do_initialize()
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"##### Spatial dimension table initialized: {elapsed_time} seconds")
        else:
            print("## SpatialDimension table exists")

        if not self.postgresql.check_table_exists('TimeDimension'):
            print("## Create time dimension tables...")
            self.postgresql.execute_sql(sql_TimeDimension)  # time table
            self.postgresql.execute_sql(sql_create_index_year)
            self.postgresql.execute_sql(sql_create_index_month)
            self.postgresql.execute_sql(sql_create_index_day)
            print("## Create time dimension tables done")
            # Time dimension initialization
            time_dim = TimeDimInitializer(self.postgresql)
            print("##### Time dimension table initializing ...")
            start_time = time.time()
            time_dim.do_initialize()
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"##### Time dimension table initialized: {elapsed_time} seconds")
        else:
            print("## TimeDimension table exists")

        if not self.postgresql.check_table_exists('FeatureDimension'):
            print("## Create feature dimension tables...")
            self.postgresql.execute_sql(sql_FeatureDimension)  # FeatureDimension table
            print("## Create feature dimension tables done")
            # feature dimension initialization
            feature_dim = FeatureDimInitializer(self.postgresql)
            print("##### FeatureDimension table initializing ...")
            start_time = time.time()
            feature_dim.do_initialize()
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"##### FeatureDimension table initialized: {elapsed_time} seconds")
        else:
            print("## FeatureDimension table exists")

        if not self.postgresql.check_table_exists('ProductDimension'):
            print("## Create prodcution dimension tables...")
            self.postgresql.execute_sql(sql_ProductDimension)  # prodcution table
            print("## Create prodcution dimension tables done")
            # prodcution dimension initialization
            pro_dim = ProductDimInitializer(self.postgresql)
            print("##### prodcution table initializing ...")
            start_time = time.time()
            pro_dim.do_initialize()
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"##### prodcution table initialized: {elapsed_time} seconds")
        else:
            print("## prodcution table exists")

        if not self.postgresql.check_table_exists('ViewpointDimension'):
            print("## Create viewpoint dimension tables...")
            self.postgresql.execute_sql(sql_ViewpointDimension)  # viewpoint table
            print("## Create viewpoint dimension tables done")
            # viewpoint dimension initialization
            vp_dim = ViewpointDimInitializer(self.postgresql)
            print("##### viewpoint table initializing ...")
            start_time = time.time()
            vp_dim.do_initialize()
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"##### viewpoint table initialized: {elapsed_time} seconds")
        else:
            print("## viewpoint table exists")


class SpatialDimInitializer:
    def __init__(self, postgresql):
        self.postgresql = postgresql

    def do_initialize(self):
        # 将地球的经纬度剖分成长和宽接近2公里*2公里的网格，并对每个网格编码（即gridCode字段）
        # ，将记录每个网格的空间范围（即gridExtent字段），并设置addressCode和addressName字段为空
        # 之后将所有的网格导入SpatialDimension表格中
        grid_size = 1  # 网格大小，单位为经纬度

        # 获取地球的经度范围和纬度范围
        min_lon, max_lon = -180, 180
        min_lat, max_lat = -90, 90

        # 清空SpatialDimension表格
        clear_table_sql = "TRUNCATE TABLE public.\"SpatialDimension\";"
        self.postgresql.execute_sql(clear_table_sql)

        # 生成网格数据
        grids = [
            (
                f"{lon_index}_{lat_index}",
                f"POLYGON(({min_lon + lon_index * grid_size} {min_lat + lat_index * grid_size}, {min_lon + (lon_index + 1) * grid_size} {min_lat + lat_index * grid_size}, {min_lon + (lon_index + 1) * grid_size} {min_lat + (lat_index + 1) * grid_size}, {min_lon + lon_index * grid_size} {min_lat + (lat_index + 1) * grid_size}, {min_lon + lon_index * grid_size} {min_lat + lat_index * grid_size}))",
                "",
                ""
            )
            for lon_index in range(int((max_lon - min_lon) / grid_size))
            for lat_index in range(int((max_lat - min_lat) / grid_size))
        ]

        # 批量插入网格数据
        insert_grid_sql = "INSERT INTO public.\"SpatialDimension\" (\"gridCode\", \"gridExtent\", \"addressCode\", \"addressName\") VALUES (%s, ST_GeomFromText(%s, 4326), %s, %s);"
        self.postgresql.execute_batch_sql(insert_grid_sql, grids)


class TimeDimInitializer:
    def __init__(self, postgresql):
        self.postgresql = postgresql

    def do_initialize(self):
        # 将1900年1月1日-2100年1月1日之间的时间，按照1天为间隔
        # 将每一天作为一条记录插入到TimeDimension表格中
        # 该表格的字段有：timeCode、year、month、day
        start_date = date(1900, 1, 1)
        end_date = date(2100, 1, 1)
        delta = timedelta(days=1)

        # 清空TimeDimension表格
        clear_table_sql = "TRUNCATE TABLE public.\"TimeDimension\";"
        self.postgresql.execute_sql(clear_table_sql)

        # 生成时间数据
        data = []
        current_date = start_date
        while current_date < end_date:
            time_code = current_date.strftime("%Y%m%d")
            year, month, day = current_date.year, current_date.month, current_date.day
            data.append((time_code, year, month, day))

            if len(data) % 20000 == 0:
                insert_time_sql = "INSERT INTO public.\"TimeDimension\" (\"timeCode\", \"year\", \"month\", \"day\") VALUES (%s, %s, %s, %s);"
                self.postgresql.execute_batch_sql(insert_time_sql, data)
                data = []

            current_date += delta

        # 处理剩余的数据
        if data:
            insert_time_sql = "INSERT INTO public.\"TimeDimension\" (\"timeCode\", \"year\", \"month\", \"day\") VALUES (%s, %s, %s, %s);"
            self.postgresql.execute_batch_sql(insert_time_sql, data)


class FeatureDimInitializer:
    def __init__(self, postgresql):
        self.postgresql = postgresql

    def do_initialize(self):
        file_path = os.path.join(os.getcwd(), "config/feature_category.yaml")
        with open(file_path, 'r') as file:
            feature_data = yaml.safe_load(file)

        clear_table_sql = 'TRUNCATE TABLE public."FeatureDimension";'
        self.postgresql.execute_sql(clear_table_sql)

        feature_records = []
        for category, features in feature_data.items():
            if category in ['NaturalGeographicFeatures', 'ArtificialGeographicFeatures']:
                for sub_features in features:
                    for feature_name, feature_info in sub_features.items():
                        feature_class = feature_info['FeatureClass']
                        feature_records.append((feature_class, feature_name))

        insert_feature_sql = 'INSERT INTO public."FeatureDimension" ("FeatureClass", "FeatureName") VALUES (%s, %s);'
        self.postgresql.execute_batch_sql(insert_feature_sql, feature_records)


class ProductDimInitializer:
    def __init__(self, postgresql):
        self.postgresql = postgresql

    def do_initialize(self):
        file_path = os.path.join(os.getcwd(), "config/product_category.yaml")
        with open(file_path, 'r') as file:
            product_data = yaml.safe_load(file)

        clear_table_sql = "TRUNCATE TABLE public.\"ProductDimension\";"
        self.postgresql.execute_sql(clear_table_sql)

        product_records = []
        for product_name, product_info in product_data.items():
            product_class = product_info['productClass']
            product_type = product_info['productType']
            crs = product_info['CRS']
            product_records.append((product_class, product_type, crs))

        insert_product_sql = "INSERT INTO public.\"ProductDimension\" (\"productClass\", \"productType\", \"CRS\") VALUES (%s, %s, %s);"
        self.postgresql.execute_batch_sql(insert_product_sql, product_records)


class ViewpointDimInitializer:
    def __init__(self, postgresql):
        self.postgresql = postgresql

    def do_initialize(self):
        rendering_ranges = [(0, 2)]
        distance = 2
        while distance < 100000:
            rendering_ranges.append((distance, distance * 2))
            distance *= 2

        clear_table_sql = "TRUNCATE TABLE public.\"ViewpointDimension\";"
        self.postgresql.execute_sql(clear_table_sql)

        viewpoint_records = []
        for level, (range_from, range_to) in enumerate(rendering_ranges, 1):
            viewpoint_records.append((str(level), str(range_from), str(range_to)))

        insert_viewpoint_sql = "INSERT INTO public.\"ViewpointDimension\" (\"viewPointLevel\", \"renderingRangeFrom\", \"renderingRangeTo\") VALUES (%s, %s, %s);"
        self.postgresql.execute_batch_sql(insert_viewpoint_sql, viewpoint_records)
