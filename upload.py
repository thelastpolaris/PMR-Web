from basehandler import BaseHandler
import tornado.web
import tornado.websocket
import os, io
from tornado_sqlalchemy import SessionMixin

from models import File
import datetime
from pytube import YouTube
import zipfile

__UPLOADS__ = "uploads/"

class FileHandler(BaseHandler):
	@tornado.web.authenticated
	async def post(self):
		user_id = int(self.get_secure_cookie("user_id"))
		mode = list(self.request.files.keys())[0]
		file_type = int(self.get_body_argument("type", default=None, strip=False))

		if not os.path.exists(__UPLOADS__):
			os.mkdir(__UPLOADS__)

		fileinfo = self.request.files[mode][0]
		fname = fileinfo['filename']
		_, fext = os.path.splitext(fname)
		fname = fname.replace(" ", "")

		folder = __UPLOADS__

		if file_type == 1:
			now = datetime.datetime.now()
			new_dir = str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second)

			folder = os.path.join(folder, new_dir)
			if not os.path.isdir(folder):
				os.mkdir(folder)
		elif file_type == 2:
			print(file_type)

		filename = os.path.join(folder, fname)

		try:
			if fext == ".zip" and file_type == 1:
				zip_file = io.BytesIO(fileinfo['body'])
				with zipfile.ZipFile(zip_file) as zip_ref:
					zip_ref.extractall(folder)
			else:
				fh = open(filename, 'wb')
				fh.write(fileinfo['body'])

			if file_type == 1:
				filename = folder

			with self.make_session() as session:
				file = File(user_id, file_type, filename)
				session.add(file)
				session.commit()
				self.write(str(file.id))
		except Exception as e:
			self.clear()
			self.set_status(500)
			self.finish(str(e))

class YouTubeHandler(tornado.websocket.WebSocketHandler, SessionMixin):
	def open(self):
		user_id = self.get_secure_cookie("user_id")

		if not user_id:
			self.write_message("Access denied")
			self.close()

	async def on_message(self, message):
		if not os.path.exists(__UPLOADS__):
			os.mkdir(__UPLOADS__)

		def progress_function(stream, chunk, file_handle, bytes_remaining):
			progress = str(int((1 - bytes_remaining / stream.filesize) * 100))
			self.write_message({"progress": progress})

		yt = YouTube(str(message), on_progress_callback=progress_function)
		resolutions = ["480p", "360p", "240p", "144p"]
		video = None

		for res in resolutions:
			video = yt.streams.filter(progressive=True, file_extension='mp4').filter(resolution = res).first()
			if video:
				break

		if video:
			await tornado.ioloop.IOLoop.current().run_in_executor(
				None,
				video.download, __UPLOADS__,
			)
			await self.write_message("finish")

			filename = os.path.join(__UPLOADS__, video.default_filename)
			user_id = int(self.get_secure_cookie("user_id"))

			with self.make_session() as session:
				file = File(user_id, 2, filename)
				session.add(file)
				session.commit()

				await self.write_message({"fileID": str(file.id)})

		self.close()

	def on_close(self):
		print("Closed")

	# self.write_message(u"You said: " + message)

	# def on_close(self):
	# 	print("WebSocket closed")