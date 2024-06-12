from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ContentType(Enum):
    COMMON_SENSE_COGNITION = "常识认知"
    SOCIAL_ETIQUETTE = "社交礼仪"
    MENTAL_INTERPRETATION = "心智解读"
    INTERESTING_STORY = "趣味故事"


class AgeGroup(Enum):
    ZERO_TO_THREE = '0-3'
    THREE_TO_SIX = '3-6'
    SIX_TO_UP = '6+'


class SortMenu(Enum):
    hot = "最热门"
    new = "最新发布"


class FirstPage(Enum):
    SORT = "排序下拉"
    AGE_GROUP = "年龄段"
    CONTENT_TYPE = "内容类型"
    NUM_FOR_PAGE = "每页显示数量"


class StoryImage(BaseModel):
    image_filename: str = ''
    image_path: str = ''


class StoryAudio(BaseModel):
    audio_filename: str = ''
    audio_path: str = ''
    duration: int = 0


class StoryTextSegment(BaseModel):
    title: str = ''
    content: str = ''
    page_num: int = 1


class StoryTextSegmentList(BaseModel):
    story_name: str = ''
    story_moral: str = ''
    role_description: str = ''
    contents: List[StoryTextSegment]


class AudioImagetext(StoryTextSegment):
    image: StoryImage
    audio: StoryAudio


class CreateStory(BaseModel):
    role: str = ''
    story_type: Optional[ContentType] = None
    age_group: Optional[AgeGroup] = None
    summary: str = ''
    story_moral: str = ''
    content_avoid: str = ''
    pages: int = Field(...)


class Story(CreateStory):
    story_name: str = ''
    cover_picture: str = ''
    favorite_count: int = 0
    like_count: int = 0
    audio_image_text: List[AudioImagetext]
    is_public: bool = False
