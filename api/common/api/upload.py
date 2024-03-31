from django.http import JsonResponse
 
#这里的函数名称开头必须小写
def upload(request):
    # 定义需要返回的数据
    data = {
        "status": "success",
        "message": "Data retrieved successfully",
        "data": {
            "user": {
                "id": 123,
                "username": "张三",
                "email": "123@qq.com"
            }
        }
    }
 
    #返回json类型数据
    return JsonResponse(data)
