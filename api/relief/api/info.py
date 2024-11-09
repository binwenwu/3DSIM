from django.http import JsonResponse


def paasInfo(request):
    # TODO: Implement the function
    data = {
        "status": "success",
        "message": "Data retrieved successfully",
        "data": {"user": {"id": 123, "username": "张三", "email": "123@qq.com"}},
    }

    # Return JSON type data
    return JsonResponse(data)
