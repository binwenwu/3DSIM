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
def query(request):
    if request.method == 'POST':
        queryParams = json.loads(request.body)
        print(queryParams)
        
        return JsonResponse({'message': 'Query successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)



    


    

    