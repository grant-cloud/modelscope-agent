import uuid
from schema.data_object import (ContentType, AgeGroup, FirstPage, SortMenu)
from schema.response import ResponseGetStories, ResponseGetStoryByID, ResponseGetScore, ResponseCreateNewStory, \
    ResponseCreateNewStoryImageAndAudio, ResponseGetTaskResult, ResponseResultMessage, ResponseGetUserStories
from schema.request import RequestCreateStory, RequestCreateImageAndAudio, RequestEnumValue
from server.generate_result import call_agent_generate_text, call_agent_generate_image_audio, get_stories_by_condition, \
    get_stories_by_condition_id, get_stories_by_condition_user, get_stories_by_condition_user_and_favorite, \
    update_user_story_to_favorite, update_story_by_condition_like_count, get_user_to_story_whether_like_result, \
    get_story_by_condition_score, get_story_gen_result, get_story_like_and_favorite_count_result, \
    get_user_to_story_whether_favorite_result, get_stories_by_condition_user_and_like, delete_story_by_id
from typing import Optional
from fastapi import Path, Depends, Query, Request, BackgroundTasks
from sqlalchemy.orm import Session
from database.models import get_db
from server.utils import create_success_result
from conf.config import ROLE_IMAGE, AUDIO_EXAMPLE


def add_router(app):
    @app.get("/story_book/get_stories",
             description="Gets all stories by specifying fields (banner, menu bar)",
             response_model=ResponseGetStories
             )
    async def get_stories(
            sort: Optional[str] = Query(None, regex="^(hot|new)$"),
            age_group: Optional[AgeGroup] = Query(None),
            story_type: Optional[ContentType] = Query(None),
            skip: int = 0,
            limit: int = 10,
            is_public: Optional[bool] = Query(True),
            db: Session = Depends(get_db)):
        """
        Get a list of stories. The default value is null. Optional field and value: My Work.
        """
        result = await get_stories_by_condition(db=db,
                                                sort=sort,
                                                age_group=age_group,
                                                story_type=story_type,
                                                is_public=is_public,
                                                skip=skip,
                                                limit=limit)

        return result

    @app.get("/story_book/get_stories/user/",
             description="Get user's all stories",
             response_model=ResponseGetUserStories
             )
    async def get_user_stories(
            request: Request,
            skip: int = 0,
            limit: int = 10,
            db: Session = Depends(get_db)):
        """
        Get a list of stories. The default value is null. Optional field and value: My Work.
        """
        user_id = request.state.user_id
        result = await get_stories_by_condition_user(db=db,
                                                     skip=skip,
                                                     limit=limit,
                                                     user_id=user_id)
        return result

    @app.get("/story_book/get_stories/{story_id}",
             description="Get a story",
             response_model=ResponseGetStoryByID
             )
    async def get_story_by_id(
            request: Request,
            story_id: int = Path(..., description="image story ID"),
            db: Session = Depends(get_db)):
        """
        Get a list of stories. The default value is null. Optional field and value: My Work.
        """
        user_id = request.state.user_id
        result = await get_stories_by_condition_id(db=db,
                                                   story_id=int(story_id),
                                                   user_id=user_id)
        return result

    @app.get("/story_book/get_stories/user/favorite",
             description="Get user's all favorite stories",
             response_model=ResponseGetStories
             )
    async def get_user_stories_favorite(
            request: Request,
            skip: int = 0,
            limit: int = 10,
            db: Session = Depends(get_db)):
        """
        Get a list of stories. The default value is null. Optional field and value: My Work.
        """
        user_id = request.state.user_id
        result = await get_stories_by_condition_user_and_favorite(db=db,
                                                                  user_id=user_id,
                                                                  skip=skip,
                                                                  limit=limit)
        return result

    @app.get("/story_book/get_stories/user/like",
             description="Get user's all like stories",
             response_model=ResponseGetStories
             )
    async def get_user_stories_like(
            request: Request,
            skip: int = 0,
            limit: int = 10,
            db: Session = Depends(get_db)):
        """
        Get a list of stories. The default value is null. Optional field and value: My Work.
        """
        user_id = request.state.user_id
        result = await get_stories_by_condition_user_and_like(db=db,
                                                              user_id=user_id,
                                                              skip=skip,
                                                              limit=limit)
        return result

    @app.get("/story_book/update/{story_id}/user/favorite",
             description="Collect a story, If the user has already added a story, cancel the story",
             response_model=ResponseResultMessage
             )
    async def add_and_cancel_story_to_favorites(
            request: Request,
            story_id: str = Path(..., title="The ID of the content to favorite"),
            db: Session = Depends(get_db)):
        user_id = request.state.user_id
        result = await update_user_story_to_favorite(db=db,
                                                     story_id=int(story_id),
                                                     user_id=user_id)
        return result

    @app.get("/story_book/update/{story_id}/user/like",
             description="update story like count",
             response_model=ResponseResultMessage
             )
    async def update_story_like_count(
            request: Request,
            story_id: str = Path(..., title="The ID of the story to like"),
            db: Session = Depends(get_db)):
        user_id = request.state.user_id
        result = await update_story_by_condition_like_count(db=db,
                                                            story_id=int(story_id),
                                                            user_id=user_id)
        return result

    @app.get("/story_book/get/user/{story_id}/like",
             description='Get whether the user likes the story')
    async def get_user_to_story_whether_like(
            request: Request,
            story_id: str = Path(..., title="The ID of the story to like"),
            db: Session = Depends(get_db)):
        user_id = request.state.user_id
        result = await get_user_to_story_whether_like_result(db=db,
                                                             story_id=int(story_id),
                                                             user_id=user_id)
        return result

    @app.get("/story_book/get/user/{story_id}/favorite",
             description='Get whether the user favorites this story')
    async def get_user_to_story_whether_favorite(
            request: Request,
            story_id: str = Path(..., title="The ID of the story to like"),
            db: Session = Depends(get_db)):
        user_id = request.state.user_id
        result = await get_user_to_story_whether_favorite_result(db=db,
                                                                 story_id=int(story_id),
                                                                 user_id=user_id)
        return result

    @app.get("/story_book/get_stories/{story_id}/count",
             description='Get the count of story favorite and like')
    async def get_story_like_and_favorite_count(
            story_id: str = Path(..., title="The ID of the story to like"),
            db: Session = Depends(get_db)):
        result = await get_story_like_and_favorite_count_result(db=db,
                                                                story_id=int(story_id))
        return result

    @app.get("/story_book/get_story_task/{task_id}",
             description="Get a story task result",
             response_model=ResponseGetTaskResult
             )
    async def get_story_task_result(task_id: str = Path(..., title="The ID of the story task"),
                                    db: Session = Depends(get_db)):
        """
        Get a story task result
        :return:
        """
        result = await get_story_gen_result(task_id=task_id, db=db)
        return result

    @app.get("/story_book/get_stories/{story_id}/score",
             description="Rate a piece of content",
             response_model=ResponseGetScore
             )
    async def get_story_score(
            story_id: str = Path(..., title="The ID of the content to rate"),
            db: Session = Depends(get_db)):
        result = await get_story_by_condition_score(db=db,
                                                    story_id=int(story_id))
        return result

    @app.delete("/story_book/delete/story/{story_id}",
                description="Delete a story")
    async def delete_story(
            request: Request,
            story_id: str = Path(..., title="The ID of the story"),
            db: Session = Depends(get_db)):
        user_id = request.state.user_id
        result = await delete_story_by_id(db=db,
                                          user_id=user_id,
                                          story_id=int(story_id))
        return result

    @app.get("/story_book/get/user/info")
    async def get_user_info(request: Request):
        return request.state.data

    @app.get("/story_book/get/prompt/{story_id}")
    async def get_prompt(story_id: str = Path(..., title="The ID of the story")):
        from server.utils import get_prompt_db
        data = get_prompt_db(story_id=int(story_id))
        result = create_success_result(message='Get Successful', data=data)
        result['story_id'] = story_id
        return result

    @app.post("/story_book/get_enum_value")
    async def get_enum_value(enum_value: RequestEnumValue):
        obj_data = RequestEnumValue.model_validate(enum_value)
        values = obj_data.model_dump().get('values')
        age_data = [{'label': f'{age.value}岁', 'value': age.value} for age in AgeGroup]
        content_data = [{'label': content.value, 'value': content.value} for content in ContentType]
        first_page_data = [{'label': first_page_field.value, 'value': first_page_field.value} for first_page_field
                           in FirstPage]
        sort_menu_data = [{'label': sort_menu_field.value, 'value': sort_menu_field.name} for sort_menu_field in
                          SortMenu]
        result = {}
        for value in values:
            if value == 'age_group':
                result['age_group'] = age_data
            elif value == 'content_type':
                result['content_type'] = content_data
            elif value == 'first_page':
                result['first_page'] = first_page_data
            elif value == 'sort_menu':
                result['sort_menu'] = sort_menu_data
            elif value == 'audio_example':
                result['audio_example'] = AUDIO_EXAMPLE
            elif value == 'role_image':
                result['role_image'] = ROLE_IMAGE

        return create_success_result(message='The constant data was successfully fetched', data=result)

    @app.post("/story_book/generate_story_text",
              description="Generate story menu",
              response_model=ResponseCreateNewStory
              )
    async def generate_story_text(
            create_story_text: RequestCreateStory):
        """
        Generate story text - story outline, avoided content, number of pages/chapters.
        """
        obj_data = RequestCreateStory.model_validate(create_story_text)
        result = await call_agent_generate_text(obj_data.model_dump())
        return result

    @app.post("/story_book/generate_story_image_and_audio",
              description="Generate story image and audio",
              response_model=ResponseCreateNewStoryImageAndAudio
              )
    async def generate_story_image_and_audio(
            request: Request,
            create_story_image_and_audio: RequestCreateImageAndAudio,
            background_tasks: BackgroundTasks,
            db: Session = Depends(get_db)):
        """
        Generate pictures ,audio and video.
        :return:
        """
        user_id = request.state.user_id
        obj_data = RequestCreateImageAndAudio.model_validate(create_story_image_and_audio)
        story_all_data = obj_data.model_dump()
        uuid_str = str(uuid.uuid4())
        background_tasks.add_task(call_agent_generate_image_audio, uuid_str, story_all_data, user_id, db)
        result = create_success_result(message='The task is running', data={'task_id': uuid_str})
        return result
