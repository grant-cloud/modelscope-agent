from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from conf.config import USER, PASSWORD, HOST, DB_NAME, PORT

# 基础的声明
Base = declarative_base()

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       pool_size=30,
                       max_overflow=20,
                       pool_recycle=1800,
                       pool_timeout=30)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=Session
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 创建数据库表
def start_create_tables(app):
    @app.on_event("startup")
    def create_tables():
        Base.metadata.create_all(engine, checkfirst=True)


# 故事表
class Story(Base):
    __tablename__ = 'stories'
    id = Column(Integer, primary_key=True, index=True)
    story_name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    story_type = Column(String(255), nullable=False)
    age_group = Column(String(255), nullable=False)
    pages = Column(Integer, nullable=False)
    is_public = Column(Boolean, default=False)
    like_count = Column(Integer, default=0, nullable=False)
    avoid_content = Column(String(255), default=None, nullable=False)
    story_moral = Column(String(255), default=None, nullable=False)
    favorite_count = Column(Integer, default=0, nullable=False)
    user_id = Column(String(255), nullable=False, index=True)
    status = Column(String(255), default=None, nullable=False)
    # 添加创建时间字段，默认值为当前时间
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    # 故事中的内容
    contents = relationship('StoryContent', back_populates='story', cascade='all, delete')
    # 故事的收藏
    favorite = relationship('Favorite', back_populates='story', cascade='all, delete')
    # 用户点赞
    like = relationship('Like', back_populates='story', cascade='all, delete')
    # 创建故事的任务id
    task = relationship('Task', back_populates='story', uselist=False, cascade='all, delete')


# 故事内容表
class StoryContent(Base):
    __tablename__ = 'story_contents'
    id = Column(Integer, primary_key=True)
    page_num = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    story = relationship('Story', back_populates='contents', cascade='all, delete')
    # 内容的图像
    image = relationship('Image', back_populates='content', uselist=False, cascade='all, delete')
    # 内容的音频
    audio = relationship('Audio', back_populates='content', uselist=False, cascade='all, delete')


# 图像表
class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    image_filename = Column(String(255), nullable=False)
    image_path = Column(String(255), nullable=False)
    content_id = Column(Integer, ForeignKey('story_contents.id'), nullable=False)
    content = relationship('StoryContent', back_populates='image', cascade='all, delete')


# 音频表
class Audio(Base):
    __tablename__ = 'audios'
    id = Column(Integer, primary_key=True)
    audio_filename = Column(String(255), nullable=False)
    audio_path = Column(String(255), nullable=False)
    content_id = Column(Integer, ForeignKey('story_contents.id'), nullable=False)
    duration = Column(Integer, default=0)
    content = relationship('StoryContent', back_populates='audio', cascade='all, delete')


# 收藏表
class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    # 关系
    story = relationship('Story', back_populates='favorite')


class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    # 关系
    story = relationship('Story', back_populates='like')


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    uuid_str = Column(String(255), nullable=False)
    create_success = Column(Boolean, default=False)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    progress = Column(Float, default=0)
    # 关系
    story = relationship('Story', back_populates='task')

