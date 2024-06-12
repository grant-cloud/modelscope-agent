from sqlalchemy.orm import Session
from sqlalchemy import desc
from schema.data_object import (ContentType, AgeGroup)
from database.models import Story, Favorite, StoryContent, Image, Audio, Task, Like
from server.utils import log_db
from server.log import logger


@log_db
def db_get_stories_condition(db: Session, order_by_condition: bool, age_group: AgeGroup, story_type: ContentType,
                             is_public: bool, skip: int, limit: int, status: str):
    condition = Story.created_at
    if order_by_condition:
        condition = Story.like_count
    if age_group:
        if story_type:
            result = db.query(Story).filter(Story.age_group == age_group, Story.story_type == story_type,
                                            Story.status == status, Story.is_public == is_public).order_by(
                desc(condition)).limit(limit).offset(skip).all()
        else:
            result = db.query(Story).filter(Story.age_group == age_group, Story.is_public == is_public,
                                            Story.status == status).order_by(
                desc(condition)).limit(limit).offset(skip).all()
    else:
        result = db.query(Story).filter(Story.is_public == is_public, Story.status == status).order_by(
            desc(condition)).limit(limit).offset(skip).all()

    return result


async def get_stories_public(db: Session, sort: str, age_group: AgeGroup, story_type: ContentType,
                             is_public: bool, skip: int = 0, limit: int = 10):
    if sort == 'hot':
        order_by_condition = True
    else:
        order_by_condition = False
    result = await db_get_stories_condition(db=db,
                                            order_by_condition=order_by_condition,
                                            age_group=age_group,
                                            story_type=story_type,
                                            is_public=is_public,
                                            skip=skip,
                                            limit=limit,
                                            status='finished'
                                            )

    return result


@log_db
def get_story_by_id(db: Session, story_id: int):
    story = db.query(Story).filter(Story.id == story_id).first()
    return story


@log_db
def update_story_status(db: Session, story_id: int, status: str):
    result = db.query(Story).filter(Story.id == story_id).update({Story.status: status})
    db.commit()
    return result


@log_db
def get_user_stories(db: Session, user_id: str, skip: int = 0,
                     limit: int = 10):
    all_user_stories = db.query(Story).filter(Story.user_id == user_id).all()
    total = len(all_user_stories)
    stories = (db.query(Story).filter(Story.user_id == user_id).order_by(desc(Story.created_at)).offset(skip).limit(
        limit).all())
    return stories, total


@log_db
def get_user_stories_sorted_by_favorite(db: Session, user_id: str, skip: int = 0, limit: int = 10):
    user_favorites = (db.query(Favorite)
                      .filter(Favorite.user_id == user_id).offset(skip).limit(limit).all())
    return user_favorites


@log_db
def get_user_stories_sorted_by_like(db: Session, user_id: str, skip: int = 0, limit: int = 10):
    user_favorites = (db.query(Like)
                      .filter(Like.user_id == user_id).offset(skip).limit(limit).all())
    return user_favorites


@log_db
def create_story(db: Session, user_id: str, story_name: str, story_moral: str, role: str,
                 story_type: str, age_group: str, pages: int, avoid_content: str,
                 is_public: bool, status: str) -> Story:
    new_story = Story(user_id=user_id, story_name=story_name, story_moral=story_moral, role=role,
                      story_type=story_type, age_group=age_group, pages=pages,
                      avoid_content=avoid_content, is_public=is_public, status=status)
    db.add(new_story)
    db.commit()
    db.refresh(new_story)
    return new_story


@log_db
def toggle_story_favorite(db: Session, user_id: str, story_id: int):
    try:
        favorite = db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.story_id == story_id).first()
        if favorite:
            story = db.query(Story).filter(Story.id == story_id).with_for_update().one()
            story.favorite_count -= 1
            db.delete(favorite)
            db.commit()
            return False
        else:
            new_favorite = Favorite(user_id=user_id, story_id=story_id)
            story = db.query(Story).filter(Story.id == story_id).with_for_update().one()
            story.favorite_count += 1
            db.add(new_favorite)
            db.commit()
            db.refresh(new_favorite)
            return True
    except Exception as e:
        logger.error(f"Failed to update story favorites， details: {e}")
        db.rollback()
    finally:
        db.close()


@log_db
def add_cancel_story_like_count(db: Session, user_id: str, story_id: int):
    try:
        like_count = db.query(Like).filter(Like.user_id == user_id, Like.story_id == story_id).first()
        if like_count:
            story = db.query(Story).filter(Story.id == story_id).with_for_update().one()
            story.like_count -= 1
            db.delete(like_count)
            db.commit()
            return False
        else:
            new_like_count = Like(user_id=user_id, story_id=story_id)
            story = db.query(Story).filter(Story.id == story_id).with_for_update().one()
            story.like_count += 1
            db.add(new_like_count)
            db.commit()
            db.refresh(new_like_count)
            return True
    except Exception as e:
        logger.error(f"Failed to update story likes， details: {e}")
        db.rollback()
    finally:
        db.close()


@log_db
def add_story_content(db: Session, story_id: int, page_num: int, title: str,
                      content: str) -> StoryContent:
    new_content = StoryContent(story_id=story_id,
                               page_num=page_num,
                               title=title,
                               content=content)
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content


@log_db
def add_story_image(db: Session, content_id: int, image_filename: str,
                    image_path: str):
    new_content_image = Image(content_id=content_id, image_filename=image_filename,
                              image_path=image_path)
    db.add(new_content_image)
    db.commit()
    db.refresh(new_content_image)
    return new_content_image


@log_db
def add_story_audio(db: Session, content_id: int, audio_filename: str,
                    audio_path: str, duration: int):
    new_content_audio = Audio(content_id=content_id, audio_filename=audio_filename,
                              audio_path=audio_path, duration=duration)
    db.add(new_content_audio)
    db.commit()
    db.refresh(new_content_audio)
    return new_content_audio


@log_db
def create_story_task(db: Session,
                      uuid_str: str,
                      story_id: int,
                      create_success: bool) -> Task:
    new_task = Task(
        uuid_str=uuid_str,
        story_id=story_id,
        create_success=create_success
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@log_db
def update_story_task(db: Session,
                      uuid_str: str,
                      create_success: bool
                      ):
    result = db.query(Task).filter(Task.uuid_str == uuid_str).update({Task.create_success: create_success})
    db.commit()
    return result


@log_db
def get_story_task(db: Session,
                   uuid_str: str):
    task = db.query(Task).filter(Task.uuid_str == uuid_str).first()
    return task


@log_db
def update_task_progress(db: Session, task_id: str, progress: float):
    task = db.query(Task).filter(Task.uuid_str == task_id).update({Task.progress: progress})
    db.commit()
    return task


@log_db
def get_user_to_story_whether_like_db(db: Session, story_id: int, user_id: str):
    result = db.query(Like).filter(Like.user_id == user_id, Like.story_id == story_id).first()
    return result


@log_db
def get_user_to_story_whether_favorite_db(db: Session, story_id: int, user_id: str):
    result = db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.story_id == story_id).first()
    return result


@log_db
def delete_story_db(db: Session,
                    user_id: str,
                    story_id: int):
    story = db.query(Story).filter(Story.user_id == user_id, Story.id == story_id).first()
    if story:
        db.delete(story)
        db.commit()
        return True
    return False
