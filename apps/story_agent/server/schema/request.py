from pydantic import BaseModel, Field
from schema.data_object import ContentType, AgeGroup, StoryTextSegment
from typing import List


class RequestCreateStory(BaseModel):
    age_group: AgeGroup = Field(...)
    story_type: ContentType = Field(...)
    role: str = ''
    summary: str = Field(...)
    story_moral: str = ''
    avoid_content: str = ''
    pages: int = 4


class RequestCreateImageAndAudio(RequestCreateStory):
    story_name: str = ''
    voice: str = ''
    role_description: str = ''
    is_public: bool = Field(...)
    contents: List[StoryTextSegment] = Field(...)


class RequestEnumValue(BaseModel):
    values: List[str] = []


class RequestCreateSpecialStory(BaseModel):
    content_type: ContentType = Field(...)
    role: str = ''
    gender: str = ''
    name: str = ''
