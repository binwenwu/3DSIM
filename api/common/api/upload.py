import json
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt 
import zipfile
import shutil
import os
from datetime import datetime
from parser.parser_3dtiles.parser_3dtiles import Parser3DTiles
from parser.parser_relief import ParserRelief
from parser.parser_physicalfield import ParserPhysicalField
from parser.parser_pointcloud import ParserPointcloud


@csrf_exempt 
def upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # 1. Extract the uploaded file to a folder
        extract_compressed_file(uploaded_file,'/home/program/3dsim/data/temp/')
        # 2. Obtain dimension information
        dimension = json.loads(request.POST.get('dimension'))
        # 3. Data parsing and storage and warehousing
        parse_and_store_data(remove_extension(uploaded_file.name),dimension)

        return JsonResponse({'message': 'Import successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)



# Data parsing and storage and warehousing
def parse_and_store_data(filename,dimension):
    # 1. Extracting information
    feature = dimension['feature']
    product = dimension['product']
    validFrom = format_date(dimension['validFrom'])
    validTo = format_date(dimension['validTo'])
    viewedRange = dimension['viewedRange']
    lon = dimension['lon']
    lat = dimension['lat']
    mimeType = dimension['mimeType']
    createTime = datetime.now().strftime('%Y%m%d')
    # 2. storage and warehousing
    if product == '3DTiles':
        path = f'/home/program/3dsim/data/temp/{filename}/tileset.json'
        p3d = Parser3DTiles()
        p3d.add_data(path,featureType=feature,createTime=createTime, validTime=[validFrom, validTo])
    elif product == 'RasterRelief':
        path = f'/home/program/3dsim/data/temp/{filename}'
        pr = ParserRelief()
        pr.add_data(mimeType = mimeType, path = path,createTime=createTime, validTime=[validFrom, validTo])
    elif product == 'PhysicalField':
        path = f'/home/program/3dsim/data/temp/{filename}'
        ppf = ParserPhysicalField()
        ppf.add_data(mimeType = mimeType, path = path,createTime=createTime, validTime=[validFrom, validTo])
    elif product == 'PointCloud':
        path = f'/home/program/3dsim/data/temp/{filename}'
        ppc = ParserPointcloud()
        ppc.add_data(mimeType = mimeType, path = path,createTime=createTime, validTime=[validFrom, validTo])
    

# Extract the uploaded file to a folder
def extract_compressed_file(uploaded_file, destination_folder):
    if uploaded_file.name.endswith('.zip'):
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            zip_ref.extractall(destination_folder)
    elif uploaded_file.name.endswith('.7z'):
        os.system(f'7z x {uploaded_file} -o{destination_folder}')
    else:
        raise ValueError('Unsupported compressed file type')
    
# Format the date to the format of yyyymmdd
def format_date(date_array):
    year = str(date_array[0])
    month = str(date_array[1]).zfill(2)
    day = str(date_array[2]).zfill(2)
    return year + month + day

# Remove the extension of the file name
def remove_extension(filename):
    if filename.endswith('.zip'):
        return filename[:-4]  
    elif filename.endswith('.7z'):
        return filename[:-3]  
    else:
        return filename
    

    