from tornado_sqlalchemy import SessionMixin, as_future
import tornado.web
import os
import av
import scipy.misc

from pipelines import createPipeline
from models import TaskDescription, Task, File
import datetime
import pytube

class TaskManager():
	__current_task_id = None
	__current_session = None

	def __init__(self):
		self.__current_task_id = None
		self.__last_session = None

	def update_task(self, current_elem, completion):
		task = self.__current_session.query(Task).filter(Task.id == self.__current_task_id).first()

		if current_elem:
			task.current_stage = current_elem

		if completion:
			task.completion = completion

		self.__current_session.add(task)
		self.__current_session.commit()

	def get_random_frame(self, path_to_video):
		container = av.open(path_to_video)
		# Get video stream
		stream = container.streams.video[0]
		decoder = container.decode(stream)
		for i, frame in enumerate(decoder):
			filename = "img/tasks/{}.png".format(self.__current_task_id)
			scipy.misc.toimage(frame.to_rgb().to_ndarray(), cmin=0.0, cmax=...).save(os.path.join("assets", filename))
			return filename

	def add_task_description(self, task, path_to_video):
		# task_description = TaskDescription(task_id=task.id)

		if task.json_data:
			persons = []
			persons_pics = []

	async def add_task(self, user_id, file_id, session):
		self.__last_session = session
		file = await as_future(session.query(File).filter(File.id == file_id).first)

		if not file:
			raise FileNotFoundError

		task = Task(user_id, file_id)
		# Update status to Processing
		task.status = 1

		session.add(task)
		session.commit()

		self.__current_task_id = task.id
		self.__current_session = session

		task.image = self.get_random_frame(file.filename)

		session.add(task)
		session.commit()

		return task.id

	async def run_task(self, task_id, session):
		task = await as_future(session.query(Task).filter(Task.id == task_id).first)
		file = await as_future(session.query(File).filter(File.id == task.file_id).first)

		self.__current_task_id = task.id
		self.__current_session = session

		JSON_data = await tornado.ioloop.IOLoop.current().run_in_executor(
			None,
			createPipeline, file.filename, self.update_task, True, True,
		)
		if JSON_data:
			task.status = 2
			task.json_data = JSON_data

			self.add_task_description(task, file.filename)
		else:
			task.status = 3

		session.add(task)
		session.commit()