from rest_framework_jwt.settings import api_settings

# 重写JWT返回结果方法
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'username':user.username,
        'id':user.id
    }

# 服务器生成jwt token, 保存当前用户的身份信息
def jwt_data_hander(user):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    # 生成jwt token数据的方法
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    # 组织payload数据
    payload = jwt_payload_handler(user)
    # 生成jwt token
    token = jwt_encode_handler(payload)
    # 给user对象增加属性，保存jwt token的数据
    user.token = token
    return user



# 返回json应答

def response_date(date, count):

    response_data = {
        "count": count,
        # 只返回年月日
        "date": date.date(),
    }
    return response_data