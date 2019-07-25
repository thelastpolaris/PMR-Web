from tornado_sqlalchemy import as_future
from basehandler import BaseHandler
import tornado.web
import os

from task import TaskManager

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
			tasks = await as_future(session.query(Task).filter(Task.user_id == user_id).all)
			files = []
			for task in tasks:
				files.append(await as_future(session.query(File).filter(File.id == task.file_id).first))

			processed_files = await as_future(session.query(Task).filter(Task.user_id == user_id).filter(Task.status == 2).count)
			inprocess_files = await as_future(session.query(Task).filter(Task.user_id == user_id).filter(Task.status != 2).count)
			processing_globally = await as_future(session.query(Task).filter(Task.status != 2).count)

			args = {
				"title": "Poor's Man Rekognition - Dashboard",
				"user": user,
				"tasks": tasks,
				"files": files,
				"processed_files": processed_files,
				"inprocess_files": inprocess_files,
				"processing_globally": processing_globally
			}

			self.render("index.html", **args)

	def post(self):
		self.set_header("Content-Type", "text/plain")
		self.write("You wrote " + self.get_body_argument("message"))


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

			self.set_status(200)
			self.finish("")
			await TaskManager().add_task(user_id, file_id, session)
