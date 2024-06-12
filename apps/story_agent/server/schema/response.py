from pydantic import BaseModel, Field
from schema.data_object import StoryTextSegment, AgeGroup, ContentType, StoryTextSegmentList
from typing import List, Union, Optional
from enum import Enum


class Status(Enum):
    SUCCESS = True
    FAIL = False


class StoryName(BaseModel):
    story_id: int
    story_name: str = ''
    status: str = ''
    task_id: str = ''
    favorite_count: int = 0
    like_count: int = 0


class GetStories(StoryName):
    cover_picture: str = ''
    pages: int = Field(...)


class ResponseResultMessage(BaseModel):
    success: Status
    message: str = ''
    data: Union[dict]


class ResponseAudioImagetext(StoryTextSegment):
    image: str = ''
    audio: str = ''
    duration: int = 0


class GetStory(StoryName):
    story_moral: str = ''
    pages: int = Field(...)
    audio_image_text: List[ResponseAudioImagetext]


class GetStoryText(StoryName):
    text: StoryTextSegment


class GetStoryImage(StoryName):
    text: StoryTextSegment


class GetStoryAudio(StoryName):
    text: StoryTextSegment


class GetStoryLikeCount(StoryName):
    like_count: int


class GetStoryScore(StoryName):
    score: float


class SpecialStory(BaseModel):
    story_name: str = ''
    cover_picture: str = ''
    story_id: int


class CreateStoryImageAndAudio(BaseModel):
    task_id: str = Field(...)


class TaskResult(BaseModel):
    task_id: str = Field(...)
    story_id: Optional[int] = None
    status: str = ''
    progress: float = 0


class ConstantFields(BaseModel):
    age: AgeGroup = Field(...)
    content: ContentType = Field(...)


class ResponseGetStories(ResponseResultMessage):
    data: Union[List[GetStories], list]


class ResponseGetUserStories(ResponseResultMessage):
    total: int = 0
    data: Union[List[GetStories], list]


class ResponseGetStoryByID(ResponseResultMessage):
    data: Union[GetStory, dict]


class ResponseGetStoryLikeCount(ResponseResultMessage):
    data: Union[GetStoryLikeCount, dict]


class ResponseGetScore(ResponseResultMessage):
    data: Union[GetStoryScore, dict]


class ResponseCreateNewStory(ResponseResultMessage):
    data: Union[StoryTextSegmentList, dict]


class ResponseCreateNewStoryImageAndAudio(ResponseResultMessage):
    data: CreateStoryImageAndAudio


class ResponseGetTaskResult(ResponseResultMessage):
    data: Union[TaskResult, dict]


class ResponseGetSpecialStory(ResponseResultMessage):
    data: Union[List[SpecialStory], list]
