from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, nullable=False)

    can_create_client = Column(Boolean, server_default='FALSE', nullable=False)
    can_create_manager = Column(Boolean, server_default='FALSE', nullable=False)

    can_get_client = Column(Boolean, server_default='FALSE', nullable=False)
    can_get_manager = Column(Boolean, server_default='FALSE', nullable=False)

    can_update_client = Column(Boolean, server_default='FALSE', nullable=False)
    can_update_manager = Column(Boolean, server_default='FALSE', nullable=False)

    can_delete_client = Column(Boolean, server_default='FALSE', nullable=False)
    can_delete_manager = Column(Boolean, server_default='FALSE', nullable=False)

    can_delete_session_client = Column(Boolean, server_default='FALSE', nullable=False)
    can_delete_session_manager = Column(Boolean, server_default='FALSE', nullable=False)

    can_create_dress = Column(Boolean, server_default='FALSE', nullable=False)
    can_get_dress = Column(Boolean, server_default='FALSE', nullable=False)
    can_update_dress = Column(Boolean, server_default='FALSE', nullable=False)
    can_delete_dress = Column(Boolean, server_default='FALSE', nullable=False)

    can_create_review = Column(Boolean, server_default='FALSE', nullable=False)
    can_get_review = Column(Boolean, server_default='FALSE', nullable=False)
    can_update_review = Column(Boolean, server_default='FALSE', nullable=False)
    can_delete_review = Column(Boolean, server_default='FALSE', nullable=False)


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    permissions = Column(Integer, ForeignKey(Permission.id), nullable=False)


class UnverifiedUser(Base):
    __tablename__ = 'unverified_users'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    reg_token = Column(String, unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey(Role.id), default=1)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    role_id = Column(Integer, ForeignKey(Role.id), nullable=False)


class Session(Base):
    __tablename__ = 'sessions'

    token = Column(String, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id))
    role_id = Column(Integer, ForeignKey(Role.id))
