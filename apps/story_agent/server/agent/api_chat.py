import os
import json
import re
import asyncio
import httpx
from dashscope.audio.tts import SpeechSynthesizer
from dashscope import ImageSynthesis
from server.log import logger
from agent.agent_config import DATA, IMAGE_DATA, dic_child_age, dic_story_type, instruction, format_str, \
    image_convert_template, DASHSCOPE_API_KEY
from server.utils import covert_url_to_local, log_async_task
from server.exception import CreateStoryError
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class AgentApi:
    def __init__(self, url="http://localhost:31512/v1/assistants/lite"):
        self.url = url
        self.headers = {"Content-Type": "application/json"}
        self.host = 'nls-gateway-cn-shanghai.aliyuncs.com'
        self.audio_url = 'https://' + self.host + '/stream/v1/tts'
        self.audio_ak = os.getenv('AUDIO_AK', None)
        self.audio_sk = os.getenv('AUDIO_SK', None)
        self.app_key = os.getenv('AUDIO_APP_KEY', None)
        self.current_dir = os.path.dirname(__file__)
        self.token_file = os.path.join(self.current_dir, 'token_file.txt')
        with open(self.token_file, 'r') as f:
            self.token = f.read()

    async def call_model(self, client, data: dict):
        logger.info("*" * 100)
        response = await client.post(self.url,
                                     headers=self.headers,
                                     data=json.dumps(data),
                                     timeout=600)
        if response.status_code != 200:
            logger.error('(gen_story): Failed to call agent to generate story text.')
        text = json.loads(response.text)
        request_id = text['request_id']
        logger.info(f'(call_model_end)Message: request_id {request_id}')
        return text

    @log_async_task('Gen story text')
    async def gen_story_text(self, content: dict):
        max_retries = 3
        retries = 0
        story_text = {}
        if not content['avoid_content']:
            avoid_content = "暴力，色情，打架"
        else:
            avoid_content = content['avoid_content']
        age_group = content['age_group'].value
        content_type = content['story_type'].value
        pages = content['pages']
        story_moral = content['story_moral']
        summary = content['summary']
        role = content['role']
        instruction_info = instruction.format(age_group=age_group,
                                              child_age_intro=dic_child_age[age_group],
                                              avoid_content=avoid_content,
                                              content_type=content_type,
                                              story_type_intro=dic_story_type[content_type],
                                              summary=summary,
                                              story_moral=story_moral,
                                              role=role
                                              )
        messages = [{
            "role": "user",
            "content": f"""生成一个对应上述主题的故事大纲，要做一个{pages}页的故事绘本，输出一个有效的JSON array of objects，参考格式
              {format_str} The JSON object:```json
              ## 注意事项
                1. "role_description": 主角形象，是主角的简短的、具体的形象描述短语，不用完整的句子，例如"一个大眼睛、短金发小男孩"，或者"一只穿背带裤的、爱笑的小熊猫"，前面不要加主角名字，只要形象描述。
              """
        }]
        DATA['agent_config']['instruction'] = instruction_info
        DATA['messages'] = messages
        text = {}
        while retries < max_retries:
            try:
                async with httpx.AsyncClient() as client:
                    text = await self.call_model(client=client, data=DATA)
                if text:
                    story = text['output']['response']
                    try:
                        pattern = r'(?<=```json\n).*?(?=\n```)'
                        matches = re.findall(pattern, story, flags=re.DOTALL)
                        story_text = json.loads(matches[0])
                    except Exception as e:
                        logger.info(e)
                        story_text = json.loads(story)
                    break
                else:
                    retries += 1
                    logger.error(f'Failed to generate story text, retry {retries} ......')
            except Exception as e:
                retries += 1
                logger.error(f'Failed to create story text, details: f{e}, text: {text}, retry {retries}............')
        return story_text

    async def gen_image_convert_text_task(self, content: dict, role: str, role_desc: str):
        DATA['agent_config']['instruction'] = image_convert_template
        max_retries = 3
        retries = 0
        messages = [{
            'role': 'user',
            'content': f'''
            ## 示例
            输入：操场的一角，阳光明媚，布布站在一旁看着远处的火车模型，眼神充满好奇。
            输出：操场，阳光，布布，远处的火车
            
            输入：火车餐厅内，布布和朋友们正在享用美味的餐点，餐厅布置温馨。
            输出：火车餐厅，美味的餐点，布布，温馨
            
            输入：在一片安静的湖边，狐狸紧紧握住八毛的手，向他表示道歉，八毛开心地笑了
            输出：湖边，狐狸，八毛，笑容
            
            输入：{content['content']}
            输出：'''
        }]
        DATA['messages'] = messages
        while retries < max_retries:
            try:
                async with httpx.AsyncClient() as client:
                    text = await self.call_model(client=client, data=DATA)
                image_convert_text = text['output']['response']
                if image_convert_text:
                    content['image_description'] = image_convert_text.replace(role, role_desc)
                    break
                else:
                    retries += 1
                    logger.error(f'Failed to generate image desc, retry {retries} ......')
            except Exception as e:
                retries += 1
                logger.error(f'Failed to convert image description，details: {e}, retry {retries} .......')
        else:
            raise CreateStoryError('IMAGE_COVERT_TEXT')
        return content

    @log_async_task('Image desc convert text')
    async def gen_image_desc_convert_text(self, story_text: dict):
        role = story_text['role']
        role_desc = story_text['role_description']
        contents = story_text['contents']
        result_list = []
        for content in contents:
            result = await self.gen_image_convert_text_task(content, role=role, role_desc=role_desc)
            result_list.append(result)
        return result_list

    async def gen_story_image(self, contents: list):
        max_retries = 3
        messages = []
        for index, content in enumerate(contents):
            retries = 0
            image_description = content['image_description']
            message = {
                "role": "user",
                "content": f"""请根据接下来的描述生成分辨率大小为720*1280图片， 使用lora来控制风格:
                 {image_description}"""
            }
            messages.append(message)
            IMAGE_DATA['messages'] = messages
            while retries < max_retries:
                try:
                    async with httpx.AsyncClient() as client:
                        text = await self.call_model(client=client, data=IMAGE_DATA)
                    image_result = text['output']['response']
                    match = re.search(r'\((https?://\S+)\)', image_result)
                    if match:
                        contents[index]["image"] = match.group(1)
                        messages.append({'role': 'assistant', 'content': image_result})
                        break
                    else:
                        retries += 1
                        logger.error(f'Failed to generate image，retry {retries} ......')
                except Exception as e:
                    retries += 1
                    logger.error(f'Failed to generate image， details: {e}, retry {retries}......')
            else:
                raise CreateStoryError('SYNC_GEN_IMAGE')
        return contents

    @log_async_task('GEN_IMAGE_TASK')
    async def gen_image_task(self, content: dict):
        max_retries = 3
        retries = 0
        image_description = content['image_description']
        size = '720*1280'
        lora_index = 'wanx1.4.5_textlora_huiben2_20240518'
        extra_input = {'lora_index': lora_index}
        loop = asyncio.get_running_loop()
        while retries < max_retries:
            try:
                response = await loop.run_in_executor(
                    None,
                    lambda: ImageSynthesis.call(
                        model='wanx-v1',
                        prompt=image_description,
                        api_key=DASHSCOPE_API_KEY,
                        size=size,
                        n=1,
                        extra_input=extra_input))
                image_result = response.output.results[0]['url']
                if image_result:
                    content["image"] = image_result
                    break
                else:
                    retries += 1
                    logger.error(f'Failed to generate image, retry {retries} ......')
            except Exception as e:
                retries += 1
                logger.error(f'Failed to generate image， details: {e}, retry {retries} ......')
        else:
            raise CreateStoryError("GEN_IMAGE_TASK")
        return content

    @log_async_task('Asynchronous image generation')
    async def gen_story_image_async(self, contents: list):
        logger.info(f"{len(contents)} requests!!!!!!!!!!!!!")
        tasks = [self.gen_image_task(content) for content in contents]
        result_list = await asyncio.gather(*tasks)
        return result_list

    async def gen_story_audio(self, contents: list, uuid_str: str):
        max_retries = 3
        loop = asyncio.get_running_loop()
        for index, content in enumerate(contents):
            retries = 0
            while retries < max_retries:
                try:
                    result = await loop.run_in_executor(
                        None,  # 使用默认的线程池执行器
                        lambda: SpeechSynthesizer.call(model='sambert-zhichu-v1',
                                                       text=content['content'],
                                                       ))
                    if result.get_audio_data():
                        audio_name = uuid_str + '-' + 'audio' + '-' + str(content['page_num']) + '.wav'
                        local_file_path = covert_url_to_local(url=result.get_audio_data(), file_name=audio_name,
                                                              local_file='audio')
                        contents[index]["audio"] = local_file_path
                        break
                    else:
                        retries += 1
                        logger.error(f'Failed to audio model, retry {retries} ......')
                except Exception as e:
                    retries += 1
                    logger.error(f'Failed to call audio model, detail: {e}')
        return contents

    async def gen_story_audio_request(self, client, text, return_format, sample_rate, voice):
        body = {
            'appkey': self.app_key,
            'token': self.token,
            'text': text,
            'format': return_format,
            'sample_rate': sample_rate,
            'voice': voice
        }
        response = await client.post(self.audio_url,
                                     headers=self.headers,
                                     data=json.dumps(body),
                                     timeout=180)
        return response

    @log_async_task('Asynchronous audio generation')
    async def gen_story_audio_call_sdk(self, contents: list, uuid_str: str, voice: str):
        if not voice:
            voice = 'zhimiao_emo'
        max_retries = 3
        for index, content in enumerate(contents):
            retries = 0
            while retries < max_retries:
                try:
                    return_format = 'wav'
                    sample_rate = 16000
                    voice = voice  # 替换成自己训练的voice
                    async with httpx.AsyncClient() as client:
                        response = await self.gen_story_audio_request(client=client,
                                                                      text=content['content'],
                                                                      return_format=return_format,
                                                                      sample_rate=sample_rate,
                                                                      voice=voice)
                    if response.status_code != 200:
                        self.token = self.request_token()
                        retries += 1
                        logger.error(f"Failed to invoke sdk to generate audio， details: {response.text}")
                        continue
                    audio_name = uuid_str + '-' + 'audio' + '-' + str(content['page_num']) + '.' + return_format
                    local_file_path = covert_url_to_local(url=response.content, file_name=audio_name,
                                                          local_file='audio')
                    contents[index]["audio"] = local_file_path
                    break
                except Exception as e:
                    retries += 1
                    logger.error(f'Failed to call audio model, detail: {e}, retry {retries}.....')
            else:
                raise CreateStoryError('GEN_AUDIO')
        return contents

    def request_token(self):
        client = AcsClient(
            self.audio_ak,
            self.audio_sk,
            "cn-shanghai"
        )
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
        request.set_version('2019-02-28')
        request.set_action_name('CreateToken')

        try:
            response = client.do_action_with_exception(request)
            text = json.loads(response)
            if 'Token' in text and 'Id' in text['Token']:
                token = text['Token']['Id']
                expire_time = text['Token']['ExpireTime']
                with open(self.token_file, 'w') as f:
                    f.write(token)
                logger.info("token = " + token)
                logger.info("expireTime = " + str(expire_time))
                return token
        except Exception as e:
            logger.error(e)
