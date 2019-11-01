def username_cookie_middleware(get_response):
    # 此处编写的代码仅在Django第一次配置和初始化的时候执行一次。
    def middleware(request):
        # 此处编写的代码会在每个请求处理视图前被调用。
        # username_cookie = request.COOKIES.get('username')
        # if username_cookie:
        #     request.delete_cookie('username')
        response = get_response(request)
        # 此处编写的代码会在每个请求处理视图之后被调用。
        return response
    return middleware