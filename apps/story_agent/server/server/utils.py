import os
import time
import asyncio
import requests
from conf.config import STATIC_FOLDER
from storage.filestorage import FileStorage
from server.log import logger
from typing import Union
from server.exception import BaseError
from filter_screen.request_screen import FilterScreen

filter_screen = FilterScreen()

file_storage = FileStorage()


def log_db(func):
    async def wrapper(*args, **kwargs):
        try:
            logger.info(f"(db)Start: DB operate start. func:{func}")
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, lambda: func(*args, **kwargs))
        except Exception as e:
            raise BaseError(f"(db)Error: DB operate Failed. detail: {e}")
        logger.info(f"(db)End: DB operate end. func:{func}")
        return result

    return wrapper


def log_async_task(prefix):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            end = time.time() - start
            logger.info(f"(Task:{prefix}), Total cost time {end}s")
            return result

        return wrapper

    return decorator


def create_success_result(message: str, data) -> dict:
    result = {
        'success': True,
        'message': message,
        'data': data
    }
    return result


def create_fail_result(message: str) -> dict:
    result = {
        'success': False,
        'message': message,
        'data': {}
    }
    return result


def covert_url_to_local(url: Union[str, bytes], file_name: str, local_file: str):
    local_path = os.path.join(STATIC_FOLDER, local_file)
    if not os.path.exists(local_path):
        os.makedirs(local_path, exist_ok=True)

    local_filename = os.path.join(local_path, file_name)
    # 将数据保存到本地文件
    if isinstance(url, str):
        response = requests.get(url)
        bin_data = response.content
    else:
        bin_data = url
    with open(local_filename, 'wb') as f:
        f.write(bin_data)
    return local_filename


root_dir = os.path.dirname(os.path.dirname(__file__))


def get_prompt_db(story_id: int):
    logs_dir = os.path.join(root_dir, "logs")
    file_list = []
    for filename in os.listdir(logs_dir):
        filepath = os.path.join(logs_dir, filename)
        if os.path.isfile(filepath):
            file_list.append(filepath)

    for filepath in file_list:
        with open(filepath, 'r') as file:
            for line in file.readlines():
                if 'description generation is complete' in line and str(story_id) in line:
                    story_desc = line.split("::")[-1]
                    return eval(story_desc)
    return {}


def filter_screen_common(content: str, check_type: str):
    try:
        if check_type == 'request_txt2txt':
            filter_result = filter_screen.request_filter_txt2txt(content=content)
        elif check_type == 'response_txt2txt':
            filter_result = filter_screen.response_filter_txt2txt(content=content)
        else:
            filter_result = filter_screen.response_filter_txt2img(url=content)
        if not filter_result['success']:
            return create_fail_result(message=filter_result['message'])
    except Exception as e:
        logger.error(f'Green network check failed, details: {e}')
        return create_fail_result(message='The green network check service is abnormal')
    return create_success_result(message=filter_result['message'], data={})
