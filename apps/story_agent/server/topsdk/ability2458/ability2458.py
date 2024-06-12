from topsdk.client import TopApiClient, BaseRequest

class Ability2458:

    def __init__(self, client: TopApiClient):
        self._client = client

    """
        钉钉商家群企业推送回调消息API
    """
    def alibaba_csis_dingdingopen_callback(self, request: BaseRequest):
        return self._client.execute(request.get_api_name(), request.to_dict(), request.get_file_param_dict())
    """
        taobao.mtee.requestservice.content.aigc.request（CRO风控API）
    """
    def taobao_mtee_requestservice_content_aigc_request(self, request: BaseRequest):
        return self._client.execute(request.get_api_name(), request.to_dict(), request.get_file_param_dict())
    """
        taobao.mtee.requestservice.rmb.request（CRO风控API）
    """
    def taobao_mtee_requestservice_activity_request(self, request: BaseRequest):
        return self._client.execute(request.get_api_name(), request.to_dict(), request.get_file_param_dict())
    """
        Mtee3 风控API（阿里云）
    """
    def taobao_mtee_requestservice_aliyun_invoke(self, request: BaseRequest):
        return self._client.execute(request.get_api_name(), request.to_dict(), request.get_file_param_dict())
    """
        taobao.mtee.requestservice.alitaobao.invoke
    """
    def taobao_mtee_requestservice_cn_invoke(self, request: BaseRequest):
        return self._client.execute(request.get_api_name(), request.to_dict(), request.get_file_param_dict())
    """
        Mtee3风控API
    """
    def taobao_mtee_requestservice_content_invoke(self, request: BaseRequest):
        return self._client.execute(request.get_api_name(), request.to_dict(), request.get_file_param_dict())
    """
        Mtee3 风控API
    """
    def taobao_mtee_requestservice_alitaobao_invoke(self, request: BaseRequest):
        return self._client.execute(request.get_api_name(), request.to_dict(), request.get_file_param_dict())
