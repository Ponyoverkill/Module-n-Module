from typing import Optional, List

from pydantic import BaseModel, validator, root_validator, Field, \
    ValidationError
from sqlalchemy import select, Column
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

import models


class UserView(BaseModel):
    id: Optional[int]
    name: str
    surname: str

    class Config:
        orm_mode = True


class User(BaseModel):
    id: Optional[int]
    email: Optional[str]
    phone: Optional[str]
    name: str
    surname: str

    async def add_user(self, session: AsyncSession):
        try:
            new_user = models.User(**self.dict())
            session.add(new_user)
            await session.commit()
            await session.close()
        except IntegrityError:
            return False

    class Config:
        orm_mode = True


class ReviewImage(BaseModel):
    id: Optional[int]
    review_id: int
    image_url: Optional[str]

    class Config:
        orm_mode = True


class Review(BaseModel):
    id: int
    user: Optional[User]
    message: Optional[str]
    rating: Optional[int]
    images: Optional[List[ReviewImage]]

    async def get_user(self, user_id: int, session: AsyncSession):
        subquery = select(models.User)
        query = subquery.where(models.User.id == user_id)
        try:
            current_user = (await session.execute(query)).scalars().one()
            self.user = UserView.from_orm(current_user)
            return self.user
        except NoResultFound:
            return None

    async def get_images(self, session: AsyncSession):
        self.images = []
        subquery = select(models.ReviewImage)
        query = subquery.where(models.ReviewImage.review_id == self.id)
        try:
            images = (await session.execute(query)).scalars().fetchall()
            for img in images:
                self.images.append(ReviewImage.from_orm(img))
            return self.images
        except NoResultFound:
            return None

    class Config:
        orm_mode = True


class Reviews(BaseModel):
    dress_id: int
    page: int
    reviews: Optional[List[Review]]

    async def from_db(self, session: AsyncSession):
        subquery = select(models.Review)
        subquery = subquery.where(models.Review.dress_id == self.dress_id)
        subquery = subquery.order_by(models.Review.id.desc())
        query = subquery.offset(3*(self.page-1)).limit(3)
        reviews = (await session.execute(query)).scalars().fetchall()
        print(reviews)
        if not reviews:
            return None
        self.reviews = []
        for review in reviews:
            current_review = Review.from_orm(review)
            await current_review.get_images(session)
            await current_review.get_user(review.user_id, session)
            self.reviews.append(current_review)
        return self.dict()

    class Config:
        orm_mode = True


class Category(BaseModel):
    id: Optional[int]
    name: Optional[str]

    async def from_db(self, session: AsyncSession, param='name'):
        subquery = select(models.Category)
        query = subquery.where(Column(param) == self.dict()[param])
        return Category.from_orm((await session.execute(query)).scalars().one())

    @root_validator
    def id_or_name_required(cls, values):
        id, name = values.get('id'), values.get('name')
        assert id or name, 'id or name required'
        return values

    class Config:
        orm_mode = True


class BaseDress(BaseModel):
    id: int
    title: Optional[str]
    description: Optional[str]
    cost: Optional[int]
    category: Optional[Category]
    rating: Optional[int]

    async def from_db(self, session: AsyncSession):
        subquery = select(models.Dress)
        query = subquery.where(models.Dress.id == self.id)
        try:
            dress_query = (await session.execute(query)).scalars().one()
            dress = BaseDress.from_orm(dress_query)
            dress.category = Category.parse_obj({'id': dress_query.category_id})
            dress.category = await dress.category.from_db(session, 'id')
            return dress
        except NoResultFound:
            raise NoResultFound
    
    class Config:
        orm_mode = True


class DressImage(BaseModel):
    id: Optional[int]
    dress_id: int
    image_url: Optional[str]

    async def from_db(self, session: AsyncSession):
        try:
            subquery = select(models.DressImage)
            query = subquery.where(models.DressImage.dress_id == self.dress_id)
            self.from_orm((await session.execute(query)).scalars())
        except NoResultFound:
            return None

    class Config:
        orm_mode = True


class DressPreview(BaseDress):
    image: Optional[DressImage]

    async def get_image(self, session: AsyncSession):
        subquery = select(models.DressImage)
        subquery = subquery.where(models.DressImage.dress_id == self.id)
        query = subquery.order_by(models.DressImage.id)
        try:
            image = (await session.execute(query)).scalars().first()
            self.image = DressImage.from_orm(image)
            return self.image
        except NoResultFound:
            return None
        except ValidationError:
            return None


class DetailView(BaseModel):
    dress: BaseDress
    images: Optional[List[DressImage]]

    async def from_db(self, session: AsyncSession):
        try:
            self.dress = await self.dress.from_db(session)
            print(self.dict())
            subquery = select(models.DressImage)
            query = subquery.where(models.DressImage.dress_id == self.dress.id)
            images = (await session.execute(query)).scalars().fetchall()
            print(images)
            self.images = []
            for img in images:
                self.images.append(DressImage.from_orm(img))
            return self.dict()
        except NoResultFound:
            return None


class ListView(BaseModel):
    page: int
    dresses: Optional[List[DressPreview]]
    category: Optional[Category]

    async def from_db(self, session: AsyncSession):
        try:
            subquery = select(models.Dress)
            if self.category:
                self.category = await self.category.from_db(session, 'name')
                subquery = subquery.where(models.Dress.category_id == self.category.id)
            query = subquery.order_by(models.Dress.id)
            query = query.offset(3*(self.page-1)).limit(3)
            dresses = (await session.execute(query)).scalars().fetchall()
            self.dresses = []
            for item in dresses:
                dress = DressPreview.from_orm(item)
                dress.category = Category.parse_obj({'id': item.category_id})
                dress.category = await dress.category.from_db(session, 'id')
                self.dresses.append(dress)
            for dress in self.dresses:
                await dress.get_image(session)
            await session.close()
            return self.dict(exclude={'category'})
        except NoResultFound:
            return None

    class Config:
        orm_mode = True

