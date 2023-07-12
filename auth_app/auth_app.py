from fastapi import FastAPI, Depends, BackgroundTasks

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse


from config import SECRET_KEY
from database import get_async_session
from schemas import RegisterUser, BaseUser, Session, ConfirmUser, User, Role

app = FastAPI(title='auth_app')


@app.middleware('http')
async def check_secret_key(request: Request,
                           call_next,
                           ):
    if 'secret-key' not in request.headers:
        return JSONResponse({'error': 'api forbidden'}, status_code=403)
    if request.headers['secret-key'] != SECRET_KEY:
        return JSONResponse({'error': 'api forbidden'}, status_code=403)
    response = await call_next(request)
    return response


@app.post('/register')
async def register(register_user: RegisterUser,
                   background_task: BackgroundTasks,
                   db_session: AsyncSession = Depends(get_async_session)
                   ):
    await register_user.hash_password()
    if register_user.email:
        user = await register_user.from_db(db_session, 'email')
        if user:
            return JSONResponse({'error': 'email already in use!'},
                                status_code=400)
        await register_user.generate_reg_token()
        return await register_user.create(db_session, background_task)
    elif register_user.phone:
        user = await register_user.from_db(db_session, 'phone')
        if user:
            return JSONResponse({'error': 'phone already in use!'},
                                status_code=400)
        return await register_user.create(db_session, background_task)
    else:
        return JSONResponse({'error': 'email or phone required!'},
                            status_code=400)


@app.post('/verify')
async def verify_user(code: ConfirmUser,
                      background_task: BackgroundTasks,
                      db_session: AsyncSession = Depends(get_async_session)
                      ):
    return await code.verify_user(db_session, background_task)


@app.post('/auth')
async def auth(session: Session,
               db_session: AsyncSession = Depends(get_async_session)
               ):
    exist_session = await session.get_session(db_session, 'token', 'model')
    if isinstance(exist_session, Session):
        result = exist_session.dict()
        print(result)
        role = Role.parse_obj({'id': result['role_id']})
        print(role)
        role = await role.get_role(db_session)
        print(role)
        result['permissions'] = await role.get_permissions(db_session)
        print(result)
        return JSONResponse(result, status_code=200)
    return JSONResponse({'auth': 'forbidden'}, status_code=403)


@app.post('/login')
async def login(user: BaseUser,
                db_session: AsyncSession = Depends(get_async_session)
                ):
    await user.hash_password()
    if user.email:
        exist_user = await user.get_user_by(db_session, 'email')
    if user.phone:
        exist_user = await user.get_user_by(db_session, 'phone')
    if not isinstance(exist_user, User):
        return JSONResponse({'error': 'Invalid login or password'},
                            status_code=401
                            )
    if user.password != exist_user.password:
        return JSONResponse({'error': 'Invalid login or password'},
                            status_code=401
                            )
    return JSONResponse({'token': await exist_user.login_user(db_session)},
                        status_code=200
                        )


@app.post('/logout')
async def logout(session: Session,
                 db_session: AsyncSession = Depends(get_async_session)
                 ):
    if session.token:
        await session.close(db_session)
    return JSONResponse({'message': 'success'}, status_code=200)


@app.delete('/delete/user')
async def delete_user(user_id: int,
                      session: Session = Depends(auth),
                      db_session: AsyncSession = Depends(get_async_session),
                      ):
    return session, user_id




if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8003)
