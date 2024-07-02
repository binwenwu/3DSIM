import os
import sys
import time
import numpy as np
import laspy
import xarray as xr
import cartopy.crs as ccrs
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from pyproj import CRS
import netCDF4 as nc
from laspy.file import File
from laspy.header import LasHeader
from bson import ObjectId
# sys.path.append("..")
from parser.parser_3dtiles.parser_3dtiles import Parser3DTiles
from parser.parser_physicalfield import ParserPhysicalField
from parser.parser_pointcloud import ParserPointcloud
from data_operations.query import Query
from data_operations.remove import Remove
from data_operations.update import Update
from pathlib import Path
from py3dtiles.tileset import TileSet
from pyhdf.SD import SD, SDC
import pprint
import h5py
import pandas as pd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling


def upload():

    pid = os.getpid() # 获取当前进程的进程ID（Process ID）
    available_cores = [i for i in range(os.cpu_count()) if i != 0] # 获取除了第一个CPU核心外的所有CPU核心编号
    os.sched_setaffinity(pid, available_cores) # 设置进程的CPU亲和性, 将进程绑定到除了第一个核心以外的所有可用核心, 以实现多核并行处理

    # 1 for add 3d tiles
    # 2 for add raster relief
    # 3 for add physical field
    # 4 for add point cloud
    mode = 1
    if mode == 1:
        p3d = Parser3DTiles()
        # _3dtilesPath = "/home/program/3dsim/data/3dtiles/New-York-Manhattan-Buildings-3D-Tiles-WGS84-Quadtree-Level-14/tileset.json"
        _3dtilesPath = "/home/program/3dsim/data/3dtiles/DA16_3D_Buildings/tileset.json"
        # _3dtilesPath = "/home/program/3dsim/data/3dtiles/白膜-武汉建筑/tileset.json"
        p3d.add_data(_3dtilesPath,featureType='Building',createTime='20230116', validTime=['19950923', '20050101'])
    pass


start_time = time.time()
upload()
end_time = time.time()
execution_time_ms = (end_time - start_time) * 1000
print(f"Code execution time:{execution_time_ms:.2f}ms")
