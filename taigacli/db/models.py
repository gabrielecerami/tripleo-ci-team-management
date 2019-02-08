from sqlalchemy import Boolean, Column, Integer, String, Date, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import JSONType

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    timestamp = Column(DateTime, primary_key=True)
    id = Column(Integer, primary_key=True)
    ref = Column(Integer)
    assigned_to = Column(Integer)
    assigned_to_name = Column(String)
    is_blocked = Column(Boolean)
    is_closed = Column(Boolean)
    owner = Column(Integer)
    owner_name = Column(String)
    subject = Column(Text)
    tags = Column(JSONType)
    QE = Column(String)
    Reviews = Column(Text)
    test_req = Column('Test Req', Text)
    status_name = Column(String)
    description = Column(Text)

class Epic(Base):
    __tablename__ = 'epics'

    timestamp = Column(DateTime, primary_key=True)
    id = Column(Integer, primary_key=True)
    ref = Column(Integer)
    owner = Column(Integer)
    owner_name = Column(String)
    tags = Column(JSONType)
    is_blocked = Column(Boolean)
    is_closed = Column(Boolean)
    subject = Column(Text)
    status = Column(Integer)
    status_name = Column(String)
    DOD = Column(Text)
    Vision = Column(Text)
    design = Column('Design and Planning', Text)
    requirements = Column('List of requirements', Text)
    description = Column(Text)

class UserStory(Base):
    __tablename__ = 'user_stories'

    timestamp = Column(DateTime, primary_key=True)
    id = Column(Integer, primary_key=True)
    ref = Column(Integer)
    owner = Column(Integer)
    owner_name = Column(String)
    tags = Column(JSONType)
    assigned_users = Column(JSONType)
    assigned_users_names = Column(JSONType)
    description = Column(Text)
    is_blocked = Column(Boolean)
    is_closed = Column(Boolean)
    subject = Column(Text)
    QE = Column(String)
    DOD = Column(Text)
    Design = Column(Text)
    Dependencies = Column(Text)
    status = Column(Integer)
    status_name = Column(String)


class Snapshot(Base):
    __tablename__ = 'snapshots'

    timestamp = Column(DateTime, primary_key=True)
    scope = Column(String)
    sprint_id = Column(Integer)

class Sprint(Base):
    __tablename__ = 'sprints'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    estimated_start = Column(Date)
    estimated_finish = Column(Date)
    watchers = Column(JSONType)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    full_name = Column(String)

model_classes = [Task, Snapshot, UserStory, Sprint, User]
