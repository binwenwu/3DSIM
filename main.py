import os
from parser.parser_3dtiles.parser_3dtiles import Parser3DTiles
from parser.parser_relief import ParserRelief
from parser.parser_physicalfield import ParserPhysicalField
from parser.parser_pointcloud import ParserPointcloud
from tools.query import Query
import time


def main():

    pid = os.getpid() # 获取当前进程的进程ID（Process ID）
    available_cores = [i for i in range(os.cpu_count()) if i != 0] # 获取除了第一个CPU核心外的所有CPU核心编号
    os.sched_setaffinity(pid, available_cores) # 设置进程的CPU亲和性, 将进程绑定到除了第一个核心以外的所有可用核心, 以实现多核并行处理

    # 1 for add 3d tiles
    # 2 for query 3d tiles
    # 3 for add raster relief
    # 4 for add physical field
    # 5 for add point cloud
    mode = 1
    if mode == 1:
        p3d = Parser3DTiles()
        testPath = "/home/program/3dsim/data/3dtiles/DA16_3D_Buildings/tileset.json"
        p3d.add_data(testPath,featureType='Building',createTime='20230116', validTime=['19950923', '20050101'])
    if mode == 2:
        ix = 0  
        query  = Query()
        result = query.query_rootSceneAsset()
        print("size of root scene: ", len(result))
        p3d = Parser3DTiles()
        p3d.save_data_to3dtiles(sceneAsset=result[ix], path='./query_tileset.json',query=query)
    if mode == 3:
        pr = ParserRelief()
        testPath = "/home/program/3dsim/data/rasterrelief/DTM_e36n31_TINRelief_4326.tif"
        pr.add_data(mimeType = 'GEOTIFF', path = testPath,createTime='20240226', validTime=['19950923', '20050101'])
    if mode == 4:
        ppf = ParserPhysicalField()
        testPath = "/home/program/3dsim/data/physicalfield/example_1.nc"
        ppf.add_data(mimeType = 'NETCDF', path = testPath,createTime='20240226', validTime=['19950923', '20050101'])
    if mode == 5:
        ppc = ParserPointcloud()
        testPath = "/home/program/3dsim/data/pointcloud/building_01.las"
        ppc.add_data(mimeType = 'LAS', path = testPath,createTime='20240226', validTime=['19950923', '20050101'])
    pass

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time_ms = (end_time - start_time) * 1000
    print(f"代码执行时间：{execution_time_ms:.2f}毫秒")
