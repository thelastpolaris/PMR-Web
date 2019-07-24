from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin

class BaseHandler(SessionMixin, RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user_id")