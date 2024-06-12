import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from server.add_router import add_router
from server.base import Server
from server.add_middleware import add_middleware
from server.config import Config
from conf.config import HTML_PATH, STORY_BOOK_ENV
from uvicorn.main import run
from database.models import start_create_tables


class FastApiserver(Server):
    def __init__(self, config: Config, **kwargs):
        super(FastApiserver, self).__init__(config=config)
        self.home_dir = os.path.dirname(os.path.dirname(__file__))
        self.templates_dir = os.path.join(self.home_dir, 'templates')
        self.app = FastAPI()
        self._host = kwargs.get('host', self._conf.server.get('host', '0.0.0.0'))
        self._port = int(kwargs.get('port', self._conf.server.get('port', '8090')))
        self.templates = Jinja2Templates(directory=self.templates_dir)
        self._add_router()
        self._add_middleware()
        self._create_tables()
        self._home()

    def _add_middleware(self):
        add_middleware(self.app)

    def _add_router(self):
        add_router(self.app)

    def _create_tables(self):
        start_create_tables(self.app)

    def _home(self):
        @self.app.get("/{path:path}", response_class=HTMLResponse)
        def redirect_to_index(path: str, request: Request):
            html_url = HTML_PATH.get(STORY_BOOK_ENV)
            return self.templates.TemplateResponse("html/index.html", {"request": request, "path": html_url})

    def run(self, *args, **kwargs):
        run(app=self.app, host=self._host, port=self._port)
