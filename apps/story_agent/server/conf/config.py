import os

# database
USER = os.getenv("DB_USER", "root")
PASSWORD = os.getenv("DB_PASSWORD", "story123")
HOST = os.getenv("DB_HOST", "localhost")
PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "story_book")

# oss
OSS_API_KEY = os.getenv("OSS_API_KEY", None)
OSS_API_SECRET = os.getenv("OSS_API_SECRET", None)
BUCKET_NAME = os.getenv("BUCKET_NAME", "modelscope-resouces")
ENDPOINT = os.getenv("ENDPOINT", None)
PREFIX = os.getenv("PREFIX", "ms-zhuixing")
STORY_BOOK_ENV = os.getenv("STORY_BOOK_ENV", "pre")

# auth
# pre
PRE_DOMAIN = "https://pre-qianwen.biz.aliyun.com/openapi/sso/v1/tongyi/info"
# production
DOMAIN = "https://qianwen.biz.aliyun.com/openapi/sso/v1/tongyi/info"

APP_KEY = os.getenv("APP_KEY", None)
BIZ_CODE = os.getenv("BIZ_CODE", None)

# static file path
STATIC_FOLDER = os.getenv("STATIC_FOLDER", "static")

AUDIO_EXAMPLE = [
    {
        "label": "宝妈",
        "audio": "https://resouces.modelscope.cn/ms-zhuixing/audio_example/zhimiao_emo_test_star.wav",
        "value": "zhimiao_emo"
    },
    {
        "label": "宝爸",
        "audio": "https://resouces.modelscope.cn/ms-zhuixing/audio_example/zhifeng_emo_test_star7.wav",
        "value": "zhifeng_emo"
    },
    {
        "label": "男童",
        "audio": "https://resouces.modelscope.cn/ms-zhuixing/audio_example/zhibei_emo_test_star.wav",
        "value": "zhibei_emo"
    },
    {
        "label": "女童",
        "audio": "https://resouces.modelscope.cn/ms-zhuixing/audio_example/sitong_test_star.wav",
        "value": "sitong"
    }
]

ROLE_IMAGE = [
    {
        'label': '小男孩',
        'value': '小男孩',
        'img': 'https://img.alicdn.com/imgextra/i3/O1CN01zDWtgC1QgnTBXVM79_!!6000000002006-2-tps-666-666.png',
    },
    {
        'label': '小女孩',
        'value': '小女孩',
        'img': 'https://img.alicdn.com/imgextra/i2/O1CN01lrOPaX1Hv9L31RoQ7_!!6000000000819-2-tps-500-500.png',
    }
]

HTML_PATH = {
    "pre": "https://dev.g.alicdn.com/catch-stars/catch-up-stars/0.0.1/",
    "prod": "https://xxxxx"
}