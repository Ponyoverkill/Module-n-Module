import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    tokens = Column(Integer, server_default='0')


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)


class Dress(Base):
    __tablename__ = 'dress'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    cost = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    rating = Column(Integer, nullable=True)


class DressImage(Base):
    __tablename__ = 'dress_images'

    id = Column(Integer, primary_key=True, nullable=False)
    dress_id = Column(Integer, ForeignKey(Dress.id), nullable=False)
    image_url = Column(String, nullable=True)


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)


class DressTag(Base):
    __tablename__ = 'dress_tags'

    id = Column(Integer, primary_key=True, nullable=True)
    dress_id = Column(Integer, ForeignKey(Dress.id))
    tag_id = Column(Integer, ForeignKey(Tag.id))


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    dress_id = Column(Integer, ForeignKey(Dress.id))
    message = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)


class ReviewImage(Base):
    __tablename__ = 'review_images'

    id = Column(Integer, primary_key=True, nullable=False)
    review_id = Column(Integer, ForeignKey(Review.id), nullable=False)
    image_url = Column(String, nullable=True)


class Status(Base):
    __tablename__ = 'statuses'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)


class Basket(Base):
    __tablename__ = 'baskets'

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    dress_id = Column(Integer, ForeignKey(Dress.id), nullable=False)
    count = Column(Integer, server_default='1', nullable=False)


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, nullable=False)
    status = Column(Integer, ForeignKey(Status.id), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow())


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    dress_id = Column(Integer, ForeignKey(Dress.id), nullable=False)
    count = Column(Integer, server_default='1', nullable=False)
