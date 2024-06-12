import os
import uuid
import json
from datetime import datetime
from topsdk.client import TopApiClient
from topsdk.ability2458.ability2458 import Ability2458
from topsdk.ability2458.request.taobao_mtee_requestservice_content_aigc_request_request import *


class FilterScreen:
    def __init__(self):
        self.filter_app_key = os.getenv('FILTER_APP_KEY', None)
        self.filter_app_sercet = os.getenv('FILTER_APP_SERCET', None)
        self.client = TopApiClient(appkey=self.filter_app_key,
                                   app_sercet=self.filter_app_sercet,
                                   top_gateway_url='http://gw.api.taobao.com/router/rest',
                                   verify_ssl=False)
        self.ability = Ability2458(client=self.client)
        self.request = TaobaoMteeRequestserviceContentAigcRequestRequest()
        self.request.code = 'aliyun_tongyi_activity_aigc_mtee_sns_unify_check'
        self.success_result = {
            'success': True,
        }
        self.failed_result = {
            'success': False
        }
        self.filter_data = {
            "firstProductName": "tongyi_activity",
            "businessName": "ali.china.aliyun_damo",
            "srcId": get_uuid(),
            "gmtCreate": create_timestamp(),
        }

    def request_filter_txt2txt(self, content: str):
        self.request.ctx = {
            "csiAigc": {
                "generateStage": 'query',
                "sceneType": 'txt2txt',
                "userInputTexts": [
                    {"content": content}
                ]
            }
        }
        self.request.ctx.update(self.filter_data)
        response = self.ability.taobao_mtee_requestservice_content_aigc_request(self.request)
        return self.analyze_result(response)

    def response_filter_txt2txt(self, content: str):
        self.request.ctx = {
            "csiAigc": {
                "generateStage": 'response',
                "sceneType": 'txt2txt',
                "userInputTexts": [
                    {"content": content}
                ]
            }
        }
        self.request.ctx.update(self.filter_data)
        response = self.ability.taobao_mtee_requestservice_content_aigc_request(self.request)
        return self.analyze_result(response)

    def response_filter_txt2img(self, url: str):
        self.request.ctx = {
            "csiAigc": {
                "generateStage": 'response',
                "sceneType": 'txt2img',
                "userInputImages": [
                    {"url": url}
                ]
            }
        }
        self.request.ctx.update(self.filter_data)
        response = self.ability.taobao_mtee_requestservice_content_aigc_request(self.request)
        return self.analyze_result(response)

    def analyze_result(self, response):
        result = json.loads(response['result'])
        if 'msg' in result:
            self.failed_result['message'] = result['msg']
        if result['code'] == 'SUCCESS':
            if result['result'] == "0" or result['result'] == "-1":
                self.success_result['message'] = 'Content conforming to specifications'
                return self.success_result
            elif result['result'] == "1":
                filed = result['riskTypeInfoList'][0]['name']
                self.failed_result['message'] = \
                    f'Content that does not meet specifications. details: trigger field {filed}'
            else:
                self.failed_result['message'] = 'This information may have illegal fields'
        return self.failed_result


def create_timestamp():
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_date


def get_uuid():
    return str(uuid.uuid4())
