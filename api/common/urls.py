from django.urls import path, include

# 通过.做相当路径导入，适用于包内导入
from .api import update, upload, query, convert
from django.shortcuts import render, HttpResponse


urlpatterns = [
    # 添加请求路由,当访问app1或者app2时会将请求交给两个模块下的urls路由
    path("upload/", upload.upload, name="upload"),
    path("query/", query.query, name="query"),
    path("update/", update.update, name="update"),
    path("convert/", convert._convert, name="convert"),
]
