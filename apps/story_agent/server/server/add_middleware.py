import requests
import os
import json
from fastapi import Request, Response
from conf.config import APP_KEY, BIZ_CODE, DOMAIN
from server.log import logger

DEBUG = os.getenv('DEBUG', True)


def add_middleware(app):
    @app.middleware('http')
    async def dashscope_custom_router(request: Request, call_next):
        paths_to_check = [
            'get_enum_value',
            'get_story_task',
            'count'
        ]
        if (any(substr in request.url.path for substr in paths_to_check)
                or '/story_book/get_stories' == request.url.path):
            response = await call_next(request)
            return response
        headers = {'Content-Type': 'application/json'}
        request_body = {
            "appKey": APP_KEY,
            "bizCode": BIZ_CODE,
            "cookies": request.cookies,
            "headers": {key: value for key, value in request.headers.items()},
            "queryParams": {}
        }
        rep = requests.post(DOMAIN, data=json.dumps(request_body), headers=headers)
        dump_data = json.dumps(rep.text)
        user_dic = json.loads(json.loads(dump_data))
        if user_dic['success']:
            request.state.user_id = user_dic['data']['userId']
            telephone = user_dic['data']['telephone']
            logger.info(f'(AUTH)User authentication success, telephone: {telephone}')
        else:
            if DEBUG:
                request.state.user_id = 'test_id'
            logger.error(f'(AUTH)User authentication failure, details: {user_dic}')
        if request.url.path == '/story_book/get/user/info':
            request.state.data = user_dic
        response = await call_next(request)
        return response
