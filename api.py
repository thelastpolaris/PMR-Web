from tornado_sqlalchemy import SessionMixin, as_future
from models import User
from tornado import escape
from basehandler import BaseHandler

class APIHandler(BaseHandler):
	async def get(self):
		self.write("PMR's API")

	async def post(self):
		with self.make_session() as session:
			self._session = session
			args, user = await self.init_API_request()

			if user:
				self.write("Welcome to API {}".format(user.login))


	async def init_API_request(self):
		args = escape.json_decode(self.request.body)
		token = args.get("access_token")

		if not token:
			self.write("No access token provided. Access denied.")
			return None, None
		else:
			token = token.encode("utf-8")

		user = await as_future(self._session.query(User).filter(User.api_token == token).first)

		if not user:
			self.write("Wrong user")
			return None, None

		return args, user


	def check_xsrf_cookie(self):
		pass