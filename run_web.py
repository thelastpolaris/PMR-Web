import tornado.ioloop
import tornado.web
from views.auth import AuthCreateHandler, AuthLoginHandler, GoogleOAuth2LoginHandler, GithubLoginHandler
from views.dashboard import DashboardHandler, UserPanelHandler, TaskHandler, TaskPageHandler
from upload import FileHandler, YouTubeHandler
from api import APIHandler, APIUploadFileHandler, APIAddTaskHandler, APITaskHandler
from tornado_sqlalchemy import make_session_factory
from tornado.web import StaticFileHandler
import os
import asyncio
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
import tornado.options
tornado.options.parse_command_line()

factory = make_session_factory("mysql://ccextractor:redwood32@localhost:3306/rekognition?charset=utf8mb4", pool_size = 1)

absFilePath = os.path.abspath(__file__)
fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)

def make_app():
	urls = [
		(r"/", DashboardHandler),
		(r"/user", UserPanelHandler),
		(r"/login", AuthLoginHandler),
		(r"/register", AuthCreateHandler),
		(r"/login_google", GoogleOAuth2LoginHandler),
		(r"/login_github", GithubLoginHandler),
		(r"/addtask", TaskHandler),
		(r"/task", TaskPageHandler),
		(r"/uploadfile", FileHandler),
		(r"/uploadyt", YouTubeHandler),
		# API
		(r"/api", APIHandler),
		(r"/api/uploadfile", APIUploadFileHandler),
		(r"/api/addtask", APIAddTaskHandler),
		(r"/api/task", APITaskHandler),
		(r"/output/(.*)", StaticFileHandler, {'path':"output/"}),

	]
	settings = {
		'template_path': os.path.join(fileDir, "templates"),
		'static_path': os.path.join(fileDir, "assets"),
		'cookie_secret': 'random',
		'session_factory': factory,
		'xsrf_cookies': True,
		'debug': True,
		'google_oauth': {
			'key': os.environ["GOOGLE_KEY"],
			'secret': os.environ["GOOGLE_SECRET"],
			'redirect_uri': 'http://fe76da5c.ngrok.io/login_google',
			'scope': ['openid', 'email', 'profile']
		},
		'github_oauth': {
			'key': os.environ["GITHUB_KEY"],
			'secret': os.environ["GITHUB_SECRET"],
			'redirect_uri': 'http://fe76da5c.ngrok.io/login_github',
			'scope': ['openid', 'email', 'profile']
		},
		'login_url': "/login"
	}
	asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
	app = tornado.web.Application(urls, **settings)

	return app

if __name__ == "__main__":
	app = make_app()
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()