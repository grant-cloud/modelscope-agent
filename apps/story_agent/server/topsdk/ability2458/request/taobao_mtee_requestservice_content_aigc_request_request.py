from typing import List
from topsdk.client import BaseRequest
from topsdk.util import convert_struct_list,convert_basic_list,convert_struct,convert_basic
from datetime import datetime


class TaobaoMteeRequestserviceContentAigcRequestRequest(BaseRequest):

    def __init__(
        self,
        code: str = None,
        ctx: dict = None
    ):
        """
            Mtee3事件code
        """
        self._code = code
        """
            Mtee3事件入参
        """
        self._ctx = ctx

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        if isinstance(code, str):
            self._code = code
        else:
            raise TypeError("code must be str")

    @property
    def ctx(self):
        return self._ctx

    @ctx.setter
    def ctx(self, ctx):
        if isinstance(ctx, dict):
            self._ctx = ctx
        else:
            raise TypeError("ctx must be dict")


    def get_api_name(self):
        return "taobao.mtee.requestservice.content.aigc.request"

    def to_dict(self):
        request_dict = {}
        if self._code is not None:
            request_dict["code"] = convert_basic(self._code)

        if self._ctx is not None:
            request_dict["ctx"] = convert_struct(self._ctx)

        return request_dict

    def get_file_param_dict(self):
        file_param_dict = {}
        return file_param_dict

