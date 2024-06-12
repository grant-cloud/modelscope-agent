import os
from server.fastapi_server import FastApiserver
from server.config import Config

# 读取本地配置文件
current_dir = os.path.dirname(__file__)
config = Config.from_file(os.path.join(current_dir, 'conf', 'base.json'))
server = FastApiserver(config=config)
app = server.app

if __name__ == '__main__':
    server.run()
