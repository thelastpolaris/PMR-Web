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

class Task(DeclarativeBase):
    __tablename__ = 'tasks'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=False)
    filename = Column(String(255), unique=False)
    json_file = Column(String(255), unique=False)
    status = Column(SmallInteger, unique=False)

    def __init__(self, user_id, filename):
        self.user_id = user_id
        self.filename = filename
        self.status = 0

