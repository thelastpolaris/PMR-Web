from sqlalchemy import BigInteger, Column, String, SmallInteger
from tornado_sqlalchemy import declarative_base
from secrets import token_hex

DeclarativeBase = declarative_base()

class User(DeclarativeBase):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    login = Column(String(255), unique=True)
    password = Column(String(255), unique=False)
    picture = Column(String(1024))
    type = Column(String(128))
    api_token = Column(String(255))

    def prettyType(self):
        if self.type == "google":
            return "Google"
        elif self.type == "github":
            return "GitHub"
        else:
            return "the website"

    def __init__(self, login, password, type, picture=None):
        self.login = login
        self.password = password
        self.picture = picture
        self.type = type

    def generateToken(self):
        self.api_token = token_hex(32)

class File(DeclarativeBase):
    __tablename__ = 'files'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=False)
    type = Column(BigInteger, unique=False)
    filename = Column(String(255), unique=False)
    extra_info = Column(String(1024), unique=False)

    def __init__(self, user_id, file_type, filename, extra_info = None):
        self.user_id = user_id
        self.type = file_type
        self.filename = filename
        self.extra_info = extra_info

class Task(DeclarativeBase):
    __tablename__ = 'tasks'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=False)
    file_id = Column(BigInteger, unique=False)
    image = Column(String(255))
    json_obj_id = Column(String(1024))
    status = Column(SmallInteger, unique=False)
    completion = Column(SmallInteger, unique=False)
    current_stage = Column(String(255))

    def __init__(self, user_id, file_id):
        self.user_id = user_id
        self.file_id = file_id
        self.image = None
        self.json_obj_id = None
        self.status = 0
        self.completion = 0
        self.current_stage = None

class TaskDescription(DeclarativeBase):
    __tablename__ = 'task_descriptions'

    id = Column(BigInteger, primary_key=True)
    task_id = Column(BigInteger, unique=False)
    persons = Column(String, unique=False)
    persons_pics = Column(String, unique=False)

    def __init__(self, task_id, persons, persons_pics):
        self.task_id = task_id
        self.persons = persons
        self.persons_pics = persons_pics