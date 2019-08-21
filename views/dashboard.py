from tornado_sqlalchemy import as_future
from basehandler import BaseHandler
import tornado.web
from settings import __UPLOADS__
import os

from bson.objectid import ObjectId

from task import TaskManager
from models import User, Task, File

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
				query_cols = (Task.id, Task.image, Task.status, Task.current_stage, Task.completion, Task.file_id)
				tasks = await as_future(session.query(*query_cols).filter(Task.user_id == user_id).all)
				tasks.reverse() # make new tasks appear earlier
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
					json_task["filename"] = file.filename
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

class TaskHandler(BaseHandler):
	@tornado.web.authenticated
	async def post(self):
		user_id = int(self.get_secure_cookie("user_id"))
		file_id = self.get_body_argument('fileID', default=None, strip=False)

		with self.make_session() as session:
			mode = self.get_argument("mode", None)
			task_manager = TaskManager(self.settings["mongo_db"])

			if mode == "add_task":
				task_id = await task_manager.add_task(user_id, file_id, session)
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
				await TaskManager(self.settings["mongo_db"]).run_task(task_id, session)
			elif mode == "rerun_task":
				task_id = self.get_argument("taskID", None)
				if task_id is not None:
					task = await as_future(session.query(Task).filter(Task.id == task_id).first)
					if task:
						if user_id == task.user_id:
							self.set_status(200)
							self.finish()

							await task_manager.run_task(task_id, session)


class TaskPageHandler(BaseHandler):
	@tornado.web.authenticated
	async def get(self):
		user_id = self.get_secure_cookie("user_id")
		task_id = self.get_argument('id',
									)

		with self.make_session() as session:
			user = await as_future(session.query(User).filter(User.id == user_id).first)

			processed_files = await as_future(session.query(Task).filter(Task.user_id == user_id).filter(Task.status == 2).count)
			inprocess_files = await as_future(session.query(Task).filter(Task.user_id == user_id).filter(Task.status != 2).count)
			processing_globally = await as_future(session.query(Task).filter(Task.status != 2).count)

			task = await as_future(session.query(Task).filter(Task.id == task_id).first)
			file = await as_future(session.query(File).filter(File.id == task.file_id).first)

			if task.user_id != int(user_id):
				self.set_status(403)
				self.write("Access Forbidden")
				self.finish()
				return

			args = {
				"title": "Poor's Man Rekognition - Task Description",
				"user": user,
				"processed_files": processed_files,
				"inprocess_files": inprocess_files,
				"processing_globally": processing_globally,
				"video_URL": self.static_url(os.path.join(__UPLOADS__.replace("assets/", ""), file.filename)),
				"image_URL": self.static_url(task.image),
				"type": "Video" if file.type == 0 or file.type == 2 else "Image",
				"name": file.filename,
				"status": task.status
			}

			self.render("task.html", **args)

	@tornado.web.authenticated
	async def post(self):
		user_id = int(self.get_secure_cookie("user_id"))
		task_id = int(self.get_argument('task_id', default=None, strip=False))

		with self.make_session() as session:
			mode = self.get_argument("mode", None)

			if mode == "get_json":
				task = await as_future(session.query(Task).filter(Task.id == task_id).first)

				if task.user_id != user_id:
					self.set_status(403)
					self.write("Access Forbidden")

				start = int(self.get_argument("start", None))
				num = int(self.get_argument("num", None))

				async def slice_json(_start, _num):
					pipelines = [{"$project": {"time_base": 1, "fps": 1, "frames": {"$slice": ["$frames", _start, _num]}}},
							 	{"$match": {"_id": ObjectId(task.json_obj_id)}}]

					async for doc in self.settings["mongo_db"].task_json.aggregate(pipelines):
						return doc

				json_data = await slice_json(0, 2)

				pts_diff = json_data["frames"][1]["pts"] - json_data["frames"][0]["pts"]
				time_base = json_data["time_base"]
				fps = json_data["fps"]

				start = int(start*fps)
				num = int(num*fps)
				print(start, num, fps)

				json_data = await slice_json(start, num)

				json_frames = []

				if json_data:
					# print(json_data)
					# json_data = json_data["frames"]

					for i in range(len(json_data["frames"]) - 1):
						frame_json = json_data["frames"][i]
						# if last_second < int(frame_json["pts"]/time_base):
						# 	last_second += 1

						json_frames.append({"second": frame_json["pts"] / time_base, "data": frame_json["faces"]})

				self.write({"frames": json_frames})