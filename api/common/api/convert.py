import json
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt 
import zipfile
import shutil
import os
import time
from parser.parser_3dtiles.parser_3dtiles import Parser3DTiles
from parser.parser_relief import ParserRelief
from parser.parser_physicalfield import ParserPhysicalField
from parser.parser_pointcloud import ParserPointcloud
from py3dtiles.convert import convert
from zipfile import ZipFile
from io import BytesIO

@csrf_exempt 
def _convert(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # 1. Extract the uploaded file to a folder
        extract_compressed_file(uploaded_file,'/home/program/3dsim/data/temp/')
        # 2. Obtain convert type information
        convert_type = json.loads(request.POST.get('convertType')).get('type')
        # 3. Data convert
        output_path = data_convert(remove_extension(uploaded_file.name),convert_type)
        # 4. Compress the converted file and return
        return compress_folder(output_path)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def data_convert(filename,convert_type):
    input_path = ""
    output_path = ""
    timestamp = time.time()
    if convert_type == "laz/las -> 3dtiles":
        input_path = f'/home/program/3dsim/data/temp/{filename}'
        output_path = f'/home/program/3dsim/data/temp/{filename}_3dtiles_{timestamp}/'
        convert(input_path,output_path)
        return output_path
    else:
        raise ValueError('Unsupported convert type')
    
    
    
# Extract the uploaded file to a folder
def extract_compressed_file(uploaded_file, destination_folder):
    if uploaded_file.name.endswith('.zip'):
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            zip_ref.extractall(destination_folder)
    elif uploaded_file.name.endswith('.7z'):
        os.system(f'7z x {uploaded_file} -o{destination_folder}')
    else:
        raise ValueError('Unsupported compressed file type')



# Remove the extension of the file name
def remove_extension(filename):
    if filename.endswith('.zip'):
        return filename[:-4]  
    elif filename.endswith('.7z'):
        return filename[:-3]  
    else:
        return filename 


# Compress folders
def compress_folder(folder_path):
    # 创建一个BytesIO对象来在内存中创建ZIP文件，避免磁盘I/O
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        # 遍历文件夹
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # 将文件相对于folder_path的相对路径作为压缩文件中的文件名
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))
    # 重置buffer的位置到开始处，以便于读取内容准备发送
    zip_buffer.seek(0)
    # 准备HTTP响应，返回ZIP文件
    response = HttpResponse(zip_buffer, content_type='application/zip')
    # 设置Content-Disposition来指示浏览器以附件形式处理，你可以根据需要修改文件名
    response['Content-Disposition'] = 'attachment; filename="folder.zip"'

    return response
        

