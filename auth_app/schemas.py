import hashlib as hash
import random
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, root_validator, validator
from sqlalchemy import select, Column
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

import models
from auth_exceptions import ConnectionToGmailException
from config import SECRET_KEY
from utils import send_verify_email, send_verify_phone, send_user
from fastapi import BackgroundTasks


class Role(BaseModel):
    id: int
    name: Optional[str]
    permissions: Optional[int]

    async def get_role(self, session: AsyncSession):
        subquery = select(models.Role)
        query = subquery.where(models.Role.id == self.id)
        try:
            role = (await session.execute(query)).scalars().one()
            return self.from_orm(role)
        except NoResultFound:
            return False

    async def get_permissions(self, session: AsyncSession):
        if not self.permissions:
            await self.get_role(session)
        subquery = select(models.Permission)
        query = subquery.where(models.Permission.id == self.permissions)
        try:
            permissions = (await session.execute(query)).scalars().one()
            permissions = permissions.__dict__
            del permissions['_sa_instance_state']
            return permissions
        except NoResultFound:
            return False

    class Config:
        orm_mode = True


class Session(BaseModel):
    token: Optional[str]
    user_id: Optional[int]
    role_id: Optional[int]

    @root_validator
    def generate_session_token(cls, values):
        token, user_id = values.get('token'), values.get('user_id')
        if not token:
            date = str(datetime.now())
            token = f'{SECRET_KEY[0:10]}{date[20:26]}{user_id}'
            token += f'{SECRET_KEY[11:]}{date[5:7]}{date[8:10]}'
            token += f'{date[11:13]}{date[14:16]}{date[17:19]}'
            token = hash.sha256(token.encode('utf-8')).hexdigest()
            values['token'] = token
        return values

    class Config:
        orm_mode = True

    async def get_session(self,
                          session: AsyncSession,
                          param: str = 'token',
                          session_type: str = 'query'
                          ):
        try:
            subquery = select(models.Session).join(models.Role)
            query = subquery.where(Column(param) == self.dict()[param])
            user_session = (await session.execute(query)).scalars().one()
            if session_type == 'model':
                return self.from_orm(user_session)
            if session_type == 'query':
                return user_session
        except NoResultFound:
            return False

    async def open(self, session: AsyncSession):
        user_session = models.Session(**self.dict())
        session.add(user_session)
        await session.commit()
        await session.close()
        return self.token

    async def close(self, session: AsyncSession):
        exist_session = await self.get_session(session, 'token', 'query')
        if isinstance(exist_session, models.Session):
            await session.delete(exist_session)
            await session.commit()
            await session.close()
        return True


class BaseUser(BaseModel):
    password: str
    email: Optional[str]
    phone: Optional[str]

    @validator('password')
    def password_complexity(cls, value):
        assert len(value) > 8, 'Too simple password'
        return value

    @root_validator
    def email_or_phone_valid(cls, values):
        email, phone = values.get('email'), values.get('phone')
        assert email or phone, 'email or phone required'
        if email and phone:
            values['phone'] = None
        if email:
            assert '@' in email, 'invalid email'
        if phone:
            assert len(phone) > 11, 'invalid phone'
        return values

    async def from_db(self, session: AsyncSession, param: str) -> models.User:
        try:
            subquery = select(models.User)
            query = subquery.where(Column(param) == self.dict()[param])
            return (await session.execute(query)).scalars().one()
        except NoResultFound:
            return False

    async def get_user_by(self, session: AsyncSession, param: str):
        try:
            subquery = select(models.User)
            query = subquery.where(Column(param) == self.dict()[param])
            user = (await session.execute(query)).scalars().one()
            return User.from_orm(user)
        except NoResultFound:
            return False

    async def hash_password(self):
        self.password = hash.sha256(self.password.encode('utf-8')).hexdigest()

    async def login_user(self, session: AsyncSession):
        print(self.dict())
        query = select(models.Role).where(models.Role.id == self.role_id)
        role = (await session.execute(query)).scalars().one()
        this_session = Session.parse_obj({'user_id': self.id,
                                          'role_id': role.id})
        print(this_session.dict())
        exist_session = await this_session.get_session(session,
                                                       'user_id',
                                                       'model'
                                                       )
        if not isinstance(exist_session, Session):
            return await this_session.open(session)
        else:
            await session.close()
            return exist_session.token


class RegisterUser(BaseUser):
    id: Optional[int]
    name: str
    surname: str
    reg_token: Optional[str]
    role_id: Optional[int]

    @validator('role_id')
    def set_defaut(cls, value):
        return 1

    async def generate_reg_token(self):
        self.reg_token = str(random.randint(10000000, 99999999))

    async def create(self, session: AsyncSession,
                     background_task: BackgroundTasks):

        for i in range(5):
            await self.generate_reg_token()
            register_user = models.UnverifiedUser(**self.dict(exclude={'id'}))
            try:
                session.add(register_user)
                await session.commit()
                break
            except IntegrityError:
                await session.rollback()
                if i == 4:
                    await session.close()
                    return JSONResponse({'register': 'reg token error!'},
                                        status_code=200)

        try:
            if self.email:
                background_task.add_task(send_verify_email,
                                         email=self.email,
                                         reg_token=self.reg_token
                                         )
                return JSONResponse({'register': 'success'},
                                    status_code=200)
            elif self.phone:
                background_task.add_task(send_verify_phone,
                                         phone=self.phone,
                                         reg_token=self.reg_token
                                         )
                return JSONResponse({'register': 'success'},
                                    status_code=200)
        except ConnectionToGmailException:
            await session.delete(register_user)
            await session.commit()
            return JSONResponse({'error': 'Connection to Gmail failure!'},
                                status_code=400)
        finally:
            await session.close()

    class Config:
        orm_mode = True


class ConfirmUser(BaseModel):
    reg_token: str

    async def verify_user(self, session: AsyncSession,
                          background_task: BackgroundTasks):
        try:
            sub_query = select(models.UnverifiedUser)
            query = sub_query.where(Column('reg_token') == self.reg_token)
            register_user = (await session.execute(query)).scalars().one()

            user = RegisterUser.from_orm(register_user)
            user = models.User(**user.dict(exclude={'id', 'reg_token'}))
            session.add(user)
            await session.delete(register_user)
            await session.commit()
            await session.refresh(user)
            new_user = User.from_orm(user)
            background_task.add_task(send_user,
                                     user=new_user.json(),
                                     url='add/user')
            return JSONResponse({'verify': 'success'},
                                status_code=200)
        except IntegrityError:
            await session.rollback()
            return JSONResponse({'error': 'this contact data already exists!'},
                                status_code=400)
        except NoResultFound:
            return JSONResponse({'error': 'Code is not valid!'},
                                status_code=400)
        except ConnectionError:
            return JSONResponse({'error': 'something goes wrong!'},
                                status_code=500)
        finally:
            await session.close()

    class Config:
        orm_mode = True


class User(BaseUser):
    id: Optional[int]
    name: str
    surname: str
    role_id: Optional[int]

    class Config:
        orm_mode = True

