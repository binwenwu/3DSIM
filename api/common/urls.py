from django.urls import path, include

# 通过.做相当路径导入，适用于包内导入
from .api import update, upload, query, convert
from django.shortcuts import render, HttpResponse


urlpatterns = [
    path("upload/", upload.upload, name="upload"),
    path("query/", query.query, name="query"),
    path("update/", update.update, name="update"),
    path("convert/", convert._convert, name="convert"),
]
