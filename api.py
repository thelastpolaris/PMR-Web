from tornado_sqlalchemy import SessionMixin
from tornado.web import RequestHandler
import json
import jwt
from models import User
import bcrypt

class APIHandler(RequestHandler):
	async def get(self):
		self.write("Hello World!")

	async def post(self):
		self.write("Hello World!")

	def check_xsrf_cookie(self):
		pass

class APIAuthHandler(SessionMixin, RequestHandler):
	def get(self):
		self.write('Auth!!')
		self.finish()

	def post(self):
		print("\n")
		print(self.request.body)
		print("\n")
		data = json.loads(self.request.body)
		try:
			login = data["username"]
			password = data["password"]
		except:
			self.set_status(403)
			return

		with self.make_session() as session:
			user = session.query(User).filter(User.login == login).filter(User.type == "user").first()
			if user:
				hashed_pass = user.password.encode("utf-8")

				if bcrypt.hashpw(password, hashed_pass) == hashed_pass:
					self.write("Welcome back, {}".format(user.login))
				else:
					self.write("Wrong Password")
			else:
				self.write("Username not found")

		if password:
			query = "SELECT id, login FROM user WHERE login = %s AND password = SHA1(%s)"
			result = self.db.get(query, login, password)

		if result is not None and result.id is not None:
			dataToken = {"id": result.id, "login": result.login}
			token = jwt.encode(dataToken, "nyxjs", algorithm='HS256')
			status = True
			res = result
		else:
			token = None
			status = False
			res = "Invalid Username or Password."

		self.write({"data": res, "result": status, "token": token})
		self.finish()

	def check_xsrf_cookie(self):
		pass