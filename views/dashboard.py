from tornado_sqlalchemy import SessionMixin, as_future
from .basehandler import BaseHandler
import tornado.web
import os

from pipelines import createPipeline
from models import User, File
import datetime
import pytube

__UPLOADS__ = "uploads/"

class DashboardHandler(SessionMixin, BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        if len(self.get_arguments("logout")) > 0:
            self.clear_all_cookies()
            self.redirect("/")
            return
        
        user_id = self.get_secure_cookie("user_id")

        with self.make_session() as session:
            user = await as_future(session.query(User).filter(User.id == user_id).first)
            files = await as_future(session.query(File).filter(File.user_id == user_id).all)

            processed_files = await as_future(session.query(File).filter(File.user_id == user_id).filter(File.status == 2).count)
            inprocess_files = await as_future(session.query(File).filter(File.user_id == user_id).filter(File.status != 2).count)
            processing_globally = await as_future(session.query(File).filter(File.status != 2).count)

            args = {
                "title": "Poor's Man Rekognition - Dashboard",
                "user": user,
                "files": files,
                "processed_files": processed_files,
                "inprocess_files": inprocess_files,
                "processing_globally": processing_globally
                }

            self.render("index.html", **args)

    def post(self):
        self.set_header("Content-Type", "text/plain")
        self.write("You wrote " + self.get_body_argument("message"))


class UserPanelHandler(SessionMixin, BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        if len(self.get_arguments("logout")) > 0:
            self.clear_all_cookies()
            self.redirect("/")
            return

        user_id = self.get_secure_cookie("user_id")

        with self.make_session() as session:
            user = await as_future(session.query(User).filter(User.id == user_id).first)

            args = {
                "title": "Poor's Man Rekognition - Dashboard",
                "user": user,
                # "get_token": self.get_token,
            }

            self.render("user_panel.html", **args)

    def check_xsrf_cookie(self):
        pass

    @tornado.web.authenticated
    def post(self):
        user_id = self.get_secure_cookie("user_id")
        if self.get_body_argument("generate_token"):
            with self.make_session() as session:
                user = session.query(User).filter(User.id == user_id).first()

                if user:
                    user.generateToken()

                    session.add(user)
                    session.commit()

                    self.write(user.api_token)
                else:
                    self.write("Wrong user")

class TaskHandler(SessionMixin, BaseHandler):
    @tornado.web.authenticated
    async def post(self):
        user_id = self.get_secure_cookie("user_id")

        if os.path.exists(__UPLOADS__) != True:
            os.mkdir(__UPLOADS__)

        youtubevideo = self.get_body_argument('youtubevideo', default=None, strip=False)
        if youtubevideo != None:
            mode = "youtubefile"
        else:
            mode = list(self.request.files.keys())[0]

        if mode == "youtubefile":
            yt = pytube.YouTube(youtubevideo)
            fname = yt.video_id

            print("Started downloading video")
            yvideo = yt.streams.filter(file_extension='mp4', resolution="360p").first()

            isFinished = await tornado.ioloop.IOLoop.current().run_in_executor(
                None,
                yvideo.download,
                __UPLOADS__,
                fname
            )

            filename = __UPLOADS__ + fname + ".mp4"
            fname = fname + ".mp4"

        else:
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

            fh = open(filename, 'wb')
            fh.write(fileinfo['body'])

        with self.make_session() as session:
            file = File(user_id, fname)
            session.add(file)
            session.commit()

            self.redirect("/")

            # Update status to pending
            file.status = 1
            session.commit()

            isImage = (mode == 'imagefile')
            if isImage:
                input_data = folder
            else:
                input_data = filename

            p = createPipeline()

            isFinished = await tornado.ioloop.IOLoop.current().run_in_executor(
                None,
                createPipeline, input_data, isImage, isImage, 1500
            )

            fname = os.path.splitext(fname)[0]

            out_extension = ''
            if isImage:
                output_file = new_dir + "_output/" + fname + "_output.jpg"
                output_json = new_dir + "_output.json"
            else:
                output_file = fname + "_output.mp4"
                output_json = fname + "_output.json"

            if isFinished:
                file.status = 2
                file.json_file = output_json
                file.output_file = output_file
                session.commit()
            else:
                file.status = 3
                session.commit()

            # file.
        # with self.make_session() as session:

