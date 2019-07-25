from tornado_sqlalchemy import as_future
from tornado import escape
from basehandler import BaseHandler
from models import File, User, Task
import urllib.request
from urllib.parse import urlparse
import os
import tornado.web
from task import TaskManager

class APIHandler(BaseHandler):
	async def get(self):
		self.write("PMR's API")

	async def post(self):
		with self.make_session() as session:
			self._session = session
			args, user = await self.init_API_request()

			if user:
				self.write({"user": user.login})

	async def init_API_request(self):
		args = escape.json_decode(self.request.body)
		token = args.get("access_token")

		if not token:
			self.write({"error": "No access token provided. Access denied."})
			return None, None
		else:
			token = token.encode("utf-8")

		user = await as_future(self._session.query(User).filter(User.api_token == token).first)

		if not user:
			self.write({"error": "Wrong user"})
			return None, None

		return args, user


	def check_xsrf_cookie(self):
		pass

class APIUploadFileHandler(APIHandler):
	async def get(self):
		self.write("PMR's API - File Uploader")

	async def post(self):
		with self.make_session() as session:
			self._session = session
			args, user = await self.init_API_request()

			if user:
				url = args.get("file_URL")
				a = urlparse(url)
				filename = os.path.join("uploads", os.path.basename(a.path))

				filename, headers = await tornado.ioloop.IOLoop.current().run_in_executor(
					None,
					urllib.request.urlretrieve, url, filename,
				)

				if filename:
					file = File(user.id, 0, filename)
					session.add(file)
					session.commit()

					json_response = {"filename": filename, "file_id": file.id}

					self.write(json_response)
				else:
					self.write({"error": "Failed to download file"})

class APIAddTaskHandler(APIHandler):
	async def get(self):
		self.write("PMR's API - File Uploader")

	async def post(self):
		with self.make_session() as session:
			self._session = session
			args, user = await self.init_API_request()

			if user:
				file_id = int(args.get("file_id").encode("utf-8"))

				task_id = await TaskManager().add_task(user.id, file_id, session)

				json_response = {"task_id": task_id}
				self.write(json_response)
				self.finish('')

				await TaskManager().run_task(task_id, session)
			else:
				self.write({"error": "Failed to download file"})

class APITaskHandler(APIHandler):
	async def get(self):
		self.write("PMR's API - File Uploader")

	async def post(self):
		with self.make_session() as session:
			self._session = session
			args, user = await self.init_API_request()

			if user:
				task_id = int(args.get("task_id").encode("utf-8"))

				task = await as_future(self._session.query(Task).filter(Task.id == task_id).first)
				file = await as_future(self._session.query(File).filter(File.id == task.file_id).first)

				json_response = dict()
				json_response["id"] = task_id
				json_response["status"] = task.status
				json_response["completion"] = task.completion
				json_response["filename"] = file.filename
				json_response["current_stage"] = task.current_stage
				json_response["json_data"] = task.json_data

				self.write(json_response)
			else:
				self.write({"error": "Failed to download file"})