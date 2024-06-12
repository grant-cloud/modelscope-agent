import os.path
from pydub import AudioSegment
from server.utils import create_fail_result, create_success_result, covert_url_to_local, filter_screen_common
from storage.filestorage import FileStorage
from sqlalchemy.orm import Session
from database.db_operation import (create_story, add_story_content, add_story_image, create_story_task, add_story_audio,
                                   get_story_task, get_stories_public, get_story_by_id, get_user_stories,
                                   get_user_stories_sorted_by_favorite, toggle_story_favorite, update_story_task,
                                   add_cancel_story_like_count, get_user_stories_sorted_by_like, delete_story_db,
                                   update_story_status, update_task_progress, get_user_to_story_whether_favorite_db,
                                   get_user_to_story_whether_like_db)
from schema.data_object import (ContentType, AgeGroup)
from agent.api_chat import AgentApi
from server.log import logger

file_storage = FileStorage()
api_chat = AgentApi()


async def add_story_content_image(content_id: int, content: dict, uuid_str: str, db: Session):
    image_name = uuid_str + '-' + 'image' + '-' + str(content['page_num']) + '.png'
    local_file_path = covert_url_to_local(url=content['image'], file_name=image_name, local_file='image')
    oss_file_path = os.path.join('images', image_name)
    file_storage.upload_file(oss_file_path=oss_file_path, file_local_path=local_file_path)
    await add_story_image(db=db, content_id=content_id, image_filename=image_name, image_path=oss_file_path)


async def add_story_content_audio(content_id: int, content: dict, uuid_str: str, db: Session):
    duration = 0
    audio_name = uuid_str + '-' + 'audio' + '-' + str(content['page_num']) + '.wav'
    oss_file_path = os.path.join('audios', audio_name)
    file_storage.upload_file(oss_file_path=oss_file_path, file_local_path=content['audio'])
    try:
        logger.info(f'(Audio Start):Calculate the duration of the audio, {audio_name}')
        audio = AudioSegment.from_file(content['audio'])
        duration = len(audio) / 1000
    except Exception as e:
        logger.error(f'(Audio Start):Failed calculate the duration of the audio, details: {e}')
    await add_story_audio(db=db, content_id=content_id, audio_filename=audio_name, audio_path=oss_file_path,
                          duration=int(duration))


async def add_content_to_db(story_id: int, content: dict, uuid_str: str, db: Session):
    story_content = await add_story_content(db=db,
                                            story_id=story_id,
                                            page_num=int(content['page_num']),
                                            title=content['title'],
                                            content=content['content'])
    story_content_id = story_content.id
    logger.info(f'Add content {story_content_id} to db successful.')
    await add_story_content_image(content_id=story_content_id, content=content, uuid_str=uuid_str, db=db)
    await add_story_content_audio(content_id=story_content_id, content=content, uuid_str=uuid_str, db=db)


async def call_agent_generate_text(gen_story_content: dict):
    """
    call agent to generate the story text.
    :return:
    """
    content = ' '.join([gen_story_content['summary'],
                        gen_story_content['story_moral'],
                        gen_story_content['avoid_content']])
    filter_result = filter_screen_common(content=content,
                                         check_type='request_txt2txt')
    if not filter_result['success']:
        return filter_result
    data = await api_chat.gen_story_text(gen_story_content)
    filter_result = filter_screen_common(content=str(data),
                                         check_type='response_txt2txt')
    if not filter_result['success']:
        return filter_result
    message = 'The story text create successfully.'
    result = create_success_result(message=message, data=data)
    if not data:
        message = 'The story text generation failed.'
        result = create_fail_result(message=message)
    return result


async def call_agent_generate_image_audio(uuid_str: str, story_all_data: dict, user_id: str,
                                          db: Session):
    """
    call agent to generate the story audio.
    :return:
    """
    try:
        voice = story_all_data['voice']
        # storage story
        story = await create_story(db=db,
                                   user_id=user_id,
                                   story_name=story_all_data['story_name'],
                                   story_moral=story_all_data['story_moral'],
                                   role=story_all_data['role'],
                                   story_type=story_all_data['story_type'],
                                   age_group=story_all_data['age_group'],
                                   pages=int(story_all_data['pages']),
                                   avoid_content=story_all_data['avoid_content'],
                                   is_public=story_all_data['is_public'],
                                   status='running')

        # create task id
        await create_story_task(db=db,
                                uuid_str=uuid_str,
                                story_id=story.id,
                                create_success=False)
        await update_task_progress(db=db,
                                   task_id=uuid_str,
                                   progress=0.2)

        contents = story_all_data['contents']
        filter_result = filter_screen_common(content=str(contents),
                                             check_type='response_txt2txt')
        if not filter_result['success']:
            await update_story_status(db=db,
                                      story_id=story.id,
                                      status='failed')
            return None
        story_contents = await api_chat.gen_image_desc_convert_text(story_all_data)
        await update_task_progress(db=db,
                                   task_id=uuid_str,
                                   progress=0.4)
        logger.info(
            f'After image description generation is complete, image generation begins. '
            f'::story_id::{story.id}::story_text::{story_contents}')
        if os.getenv("ASYNC_GEN_IMAGE", 'async') == 'async':
            logger.info("--------------Use asynchronous methods to generate images.--------------------------")
            data_image = await api_chat.gen_story_image_async(contents=story_contents)
        else:
            logger.info("--------------Use synchronization methods to generate images.-----------------------")
            data_image = await api_chat.gen_story_image(contents=story_contents)
        await update_task_progress(db=db,
                                   task_id=uuid_str,
                                   progress=0.5)
        for content_image in data_image:
            image_url = content_image['image']
            filter_result = filter_screen_common(content=image_url,
                                                 check_type='response_txt2img')
            if not filter_result['success']:
                return filter_result
        await update_task_progress(db=db,
                                   task_id=uuid_str,
                                   progress=0.6)
        logger.info(f'After image generation is complete, voice generation begins. data_image:{data_image}')
        if os.getenv('GEN_AUDIO_METHOD', 'dashscope') == 'dashscope':
            contents = await api_chat.gen_story_audio(contents=data_image, uuid_str=uuid_str)
        else:
            contents = await api_chat.gen_story_audio_call_sdk(contents=data_image, uuid_str=uuid_str, voice=voice)
        await update_task_progress(db=db,
                                   task_id=uuid_str,
                                   progress=0.8)
        logger.info(f'Audio generation complete, detail: {contents}')

        # storage story content
        for content in contents:
            logger.info(f'Start adding content={content} to the database')
            await add_content_to_db(story_id=story.id, content=content, uuid_str=uuid_str, db=db)
            logger.info(f'Finish adding content={content} to the database')
        # update task result
        await update_story_task(db=db,
                                uuid_str=uuid_str,
                                create_success=True)
        # update story status
        await update_story_status(db=db,
                                  story_id=story.id,
                                  status='finished')
        await update_task_progress(db=db,
                                   task_id=uuid_str,
                                   progress=1.0)
        logger.info("Congratulations on your story creation.......")
    except Exception as e:
        await update_story_status(db=db,
                                  story_id=story.id,
                                  status='failed')
        logger.error(f"(Finished)Failed to generate audio for story image, details: {e}")


async def get_story_gen_result(db: Session, task_id: str):
    task = await get_story_task(db=db,
                                uuid_str=task_id)
    story_id = ''
    story_status = ''
    story_progress = ''
    if task is None:
        message = f'The task {task_id} is not exist.'
    elif task.create_success:
        message = f"The task {task_id} is successful and story create successfully."
        story_id = task.story.id
        story_status = task.story.status
        story_progress = task.progress
    else:
        message = f"The task  {task_id} is running."
        story_id = task.story.id
        story_status = task.story.status
        story_progress = task.progress
    data = {
        'task_id': task_id,
        'story_id': story_id,
        'status': story_status,
        'progress': story_progress
    }
    return create_success_result(message=message, data=data)


async def get_stories_by_condition(sort: str, age_group: AgeGroup, story_type: ContentType, skip: int, limit: int,
                                   is_public: bool, db: Session):
    stories = await get_stories_public(db=db,
                                       sort=sort,
                                       age_group=age_group,
                                       story_type=story_type,
                                       skip=skip,
                                       limit=limit,
                                       is_public=is_public
                                       )

    message = "Get stories by condition is successful."
    data = []
    if stories:
        for story in stories:
            temp = {
                'story_id': story.id,
                'story_name': story.story_name,
                'cover_picture': file_storage.cover_to_url(story.contents[0].image.image_path, small_image=True),
                'favorite_count': story.favorite_count,
                'pages': story.pages,
                'status': story.status,
                'task_id': story.task.uuid_str,
                'like_count': story.like_count
            }
            data.append(temp)

    return create_success_result(message=message, data=data)


async def get_stories_by_condition_id(db: Session, story_id: int, user_id: str):
    story = await get_story_by_id(db=db,
                                  story_id=story_id)

    data = {}
    message = f'The story {story_id} not exist.'
    if not story:
        return create_success_result(message=message, data=data)
    if story.user_id == user_id or story.is_public:
        if story.status == 'finished':
            contents = story.contents
            res_contents = []
            for story_content in contents:
                temp = {
                    'title': story_content.title,
                    'content': story_content.content,
                    'page_num': story_content.page_num,
                    'image': file_storage.cover_to_url(story_content.image.image_path),
                    'audio': file_storage.cover_to_url(story_content.audio.audio_path),
                    'duration': story_content.audio.duration
                }
                res_contents.append(temp)
            data = {
                'story_id': story.id,
                'story_name': story.story_name,
                'story_moral': story.story_moral,
                'pages': story.pages,
                'audio_image_text': res_contents,
                'status': story.status,
                'task_id': story.task.uuid_str,
                'favorite_count': story.favorite_count,
                'like_count': story.like_count
            }
        else:
            data = {
                'story_id': story.id,
                'story_name': story.story_name,
                'story_moral': story.story_moral,
                'pages': story.pages,
                'audio_image_text': [],
                'status': story.status,
                'task_id': story.task.uuid_str,
                'favorite_count': story.favorite_count,
                'like_count': story.like_count
            }
        message = f"Get story by id={story_id} is successful."
    return create_success_result(message=message, data=data)


async def get_stories_by_condition_user(db: Session,
                                        user_id: str,
                                        limit: int,
                                        skip: int):
    stories, total = await get_user_stories(db=db,
                                            user_id=user_id,
                                            skip=skip,
                                            limit=limit)
    message = "Get stories by condition user is successful. Result is None."
    data = []
    if stories:
        for story in stories:
            if story.status == 'finished':
                temp = {
                    'story_id': story.id,
                    'story_name': story.story_name,
                    'cover_picture': file_storage.cover_to_url(story.contents[0].image.image_path, small_image=True),
                    'favorite_count': story.favorite_count,
                    'pages': story.pages,
                    'status': story.status,
                    'task_id': story.task.uuid_str,
                    'like_count': story.like_count
                }
            else:
                temp = {
                    'story_id': story.id,
                    'story_name': story.story_name,
                    'cover_picture': '',
                    'favorite_count': story.favorite_count,
                    'pages': story.pages,
                    'status': story.status,
                    'task_id': story.task.uuid_str,
                    'like_count': story.like_count
                }
            data.append(temp)
        message = "Get stories by condition user is successful."
    result = create_success_result(message=message, data=data)
    result['total'] = total
    return result


async def update_user_story_to_favorite(db: Session,
                                        story_id: int,
                                        user_id: str):
    result = await toggle_story_favorite(db=db,
                                         user_id=user_id,
                                         story_id=story_id)
    if result:
        message = "Add user favorites stories successfully."
    else:
        message = "remove user favorites stories successfully."
    if result is None:
        message = f"The story {story_id} is not exist."

    return create_success_result(message=message, data={})


async def get_stories_by_condition_user_and_favorite(db: Session,
                                                     limit: int,
                                                     skip: int,
                                                     user_id: str):
    user_favorites = await get_user_stories_sorted_by_favorite(db=db,
                                                               user_id=user_id,
                                                               skip=skip,
                                                               limit=limit)
    message = "the stories is None."
    data = []
    if user_favorites:
        for obj_story in user_favorites:
            story = obj_story.story
            temp = {
                'story_id': story.id,
                'story_name': story.story_name,
                'cover_picture': file_storage.cover_to_url(story.contents[0].image.image_path, small_image=True),
                'favorite_count': story.favorite_count,
                'pages': story.pages,
                'status': story.status,
                'task_id': story.task.uuid_str,
                'like_count': story.like_count
            }
            data.append(temp)
            message = "Get stories by condition user favorite is successful."

    return create_success_result(message=message, data=data)


async def get_stories_by_condition_user_and_like(db: Session,
                                                 limit: int,
                                                 skip: int,
                                                 user_id: str):
    user_likes = await get_user_stories_sorted_by_like(db=db,
                                                       user_id=user_id,
                                                       skip=skip,
                                                       limit=limit)
    message = "the stories is None."
    data = []
    if user_likes:
        for obj_story in user_likes:
            story = obj_story.story
            temp = {
                'story_id': story.id,
                'story_name': story.story_name,
                'cover_picture': file_storage.cover_to_url(story.contents[0].image.image_path, small_image=True),
                'favorite_count': story.favorite_count,
                'pages': story.pages,
                'status': story.status,
                'task_id': story.task.uuid_str,
                'like_count': story.like_count
            }
            data.append(temp)
            message = "Get stories by condition user like is successful."

    return create_success_result(message=message, data=data)


async def update_story_by_condition_like_count(db: Session,
                                               story_id: int,
                                               user_id: str):
    result = await add_cancel_story_like_count(db=db,
                                               user_id=user_id,
                                               story_id=story_id)
    if result:
        message = "Add user like stories successfully."
    else:
        message = "remove user like stories successfully."
    if result is None:
        message = f"The story {story_id} is not exist."

    return create_success_result(message=message,
                                 data={})


async def get_story_by_condition_score(db: Session,
                                       story_id: int):
    story = await get_story_by_id(db=db,
                                  story_id=story_id)
    data = {}
    message = 'the story is not exist.'
    if story:
        score = story.score
        data = {
            'story_id': story.id,
            'story_name': story.story_name,
            'task_id': story.task.uuid_str,
            'status': story.status,
            'score': score
        }
        message = 'The story was successfully queried.'
    return create_success_result(message=message,
                                 data=data)


async def get_user_to_story_whether_like_result(db: Session,
                                                story_id: int,
                                                user_id: str):
    flag = False
    message = 'User unlikes the current story.'
    like_flag = await get_user_to_story_whether_like_db(db=db,
                                                        story_id=story_id,
                                                        user_id=user_id)
    if like_flag:
        flag = True
        message = 'User like the current story.'
    return create_success_result(message=message,
                                 data={'is_like': flag})


async def get_user_to_story_whether_favorite_result(db: Session,
                                                    story_id: int,
                                                    user_id: str):
    flag = False
    message = 'User remove the current story from favorite.'
    like_flag = await get_user_to_story_whether_favorite_db(db=db,
                                                            story_id=story_id,
                                                            user_id=user_id)
    if like_flag:
        flag = True
        message = 'User favorite the current story.'
    return create_success_result(message=message,
                                 data={'is_favorite': flag})


async def get_story_like_and_favorite_count_result(db: Session,
                                                   story_id: int):
    story = await get_story_by_id(db=db,
                                  story_id=story_id)

    data = {}
    message = f'The story {story_id} not exist.'
    if not story:
        return create_success_result(message=message, data=data)
    if story.is_public:
        data = {
            'story_id': story.id,
            'status': story.status,
            'task_id': story.task.uuid_str,
            'favorite_count': story.favorite_count,
            'like_count': story.like_count
        }
        message = f"Get story by id {story_id} is successful."
    return create_success_result(message=message, data=data)


async def delete_story_by_id(db: Session,
                             user_id: str,
                             story_id: int):
    result = await delete_story_db(db=db,
                                   user_id=user_id,
                                   story_id=story_id)
    message = 'The current story does not belong to you and cannot be deleted'
    if result:
        message = 'Successfully deleted'
    return create_success_result(message=message, data={})
