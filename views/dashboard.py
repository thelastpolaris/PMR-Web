from tornado_sqlalchemy import as_future
from basehandler import BaseHandler
import tornado.web
import os

from task import TaskManager
from tornado import escape

from pipelines import createPipeline
from models import User, Task, File
import datetime
import pytube

__UPLOADS__ = "uploads/"

class DashboardHandler(BaseHandler):
	@tornado.web.authenticated
	async def get(self):
		if len(self.get_arguments("logout")) > 0:
			self.clear_all_cookies()
			self.redirect("/")
			return

		user_id = self.get_secure_cookie("user_id")

		with self.make_session() as session:
			user = await as_future(session.query(User).filter(User.id == user_id).first)

			processed_files = await as_future(session.query(Task).filter(Task.user_id == user_id).filter(Task.status == 2).count)
			inprocess_files = await as_future(session.query(Task).filter(Task.user_id == user_id).filter(Task.status != 2).count)
			processing_globally = await as_future(session.query(Task).filter(Task.status != 2).count)

			args = {
				"title": "Poor's Man Rekognition - Dashboard",
				"user": user,
				"processed_files": processed_files,
				"inprocess_files": inprocess_files,
				"processing_globally": processing_globally
			}

			self.render("index.html", **args)

	@tornado.web.authenticated
	async def post(self):
		user_id = self.get_secure_cookie("user_id")

		with self.make_session() as session:
			mode = self.get_argument("mode", None)

			if mode == "list":
				tasks = await as_future(session.query(Task).filter(Task.user_id == user_id).all)
				num_all_tasks = len(tasks)
				json_tasks = []

				start_i = int(self.get_argument("start", None))
				amount = int(self.get_argument("amount", None))

				if start_i is not None and amount:
					tasks = tasks[start_i:(start_i + amount)]

				for task in tasks:
					file = await as_future(session.query(File).filter(File.id == task.file_id).first)
					json_task = dict()
					json_task["task_id"] = task.id
					json_task["image_url"] = self.static_url(task.image)
					json_task["filename"] = file.filename.split("/")[-1]
					json_task["status"] = task.status
					json_task["current_stage"] = task.current_stage
					json_task["completion"] = task.completion

					json_tasks.append(json_task)

				json_response = {"tasks": json_tasks, "num_all_tasks": num_all_tasks}
				self.write(json_response)
			elif mode == "delete":
				task_id = int(self.get_argument("task_id", None))

				task = await as_future(session.query(Task).filter(Task.id == task_id).first)
				if task:
					session.delete(task)

				self.set_status(200)

				json_response = {"status": "success"}
				self.write(json_response)

class UserPanelHandler(BaseHandler):
	@tornado.web.authenticated
	async def get(self):
		if len(self.get_arguments("logout")) > 0:
			self.clear_all_cookies()
			self.redirect("/")
			return

		user_id = self.get_secure_cookie("user_id")

		with self.make_session() as session:
			user = await as_future(session.query(User).filter(User.id == user_id).first)
			user_files = await as_future(session.query(File).filter(File.user_id == User.id).filter)

			video_count = await as_future(user_files.filter(File.type == 0).count)
			img_count = await as_future(user_files.filter(File.type == 1).count)
			yt_count = await as_future(user_files.filter(File.type == 2).count)

			args = {
				"title": "Poor's Man Rekognition - Dashboard",
				"user": user,
				"video_count": video_count,
				"img_count": img_count,
				"yt_count": yt_count,
			}

			self.render("user_panel.html", **args)

	def check_xsrf_cookie(self):
		pass

	@tornado.web.authenticated
	def post(self):
		user_id = self.get_secure_cookie("user_id")
		if self.get_argument("generate_token"):
			with self.make_session() as session:
				user = session.query(User).filter(User.id == user_id).first()

				if user:
					user.generateToken()

					session.add(user)
					session.commit()

					self.write(user.api_token)
				else:
					self.write("Wrong user")

class FileHandler(BaseHandler):
	@tornado.web.authenticated
	async def post(self):
		user_id = int(self.get_secure_cookie("user_id"))
		mode = list(self.request.files.keys())[0]

		if not os.path.exists(__UPLOADS__):
			os.mkdir(__UPLOADS__)

		fileinfo = self.request.files[mode][0]
		fname = fileinfo['filename']
		fname = fname.replace(" ", "")

		folder = __UPLOADS__

		if mode == "imagefile":
			now = datetime.datetime.now()
			new_dir = str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second)

			folder = folder + new_dir + "/"
			if os.path.isdir(folder) == False:
				os.mkdir(folder)

		filename = folder + fname

		try:
			fh = open(filename, 'wb')
			fh.write(fileinfo['body'])

			with self.make_session() as session:
				file_type = int(mode is "imagefile")

				file = File(user_id, file_type, filename)
				session.add(file)
				session.commit()
				self.write(str(file.id))
		except Exception as e:
			self.clear()
			self.set_status(500)
			self.finish(str(e))

class TaskHandler(BaseHandler):
	@tornado.web.authenticated
	async def post(self):
		user_id = self.get_secure_cookie("user_id")
		file_id = self.get_body_argument('fileID', default=None, strip=False)

		with self.make_session() as session:
			task_id = await TaskManager().add_task(user_id, file_id, session)
			self.set_status(200)

			task = await as_future(session.query(Task).filter(Task.id == task_id).first)
			file = await as_future(session.query(File).filter(File.id == task.file_id).first)

			json_task = {"image_url": self.static_url(task.image),
						 "filename": file.filename.split("/")[-1],
						 "status": task.status,
						 "current_stage": task.current_stage,
						 "completion": task.completion
			}

			self.finish(json_task)
			await TaskManager().run_task(task_id, session)