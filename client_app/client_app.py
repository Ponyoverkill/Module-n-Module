import json
import time

from fastapi import FastAPI, Request, Depends
from fastapi.responses import StreamingResponse
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTask
import httpx
from starlette.responses import Response, JSONResponse


from utils import redis_check, redis_cache
from database import get_async_session
from schemas import Category, User, ListView, DetailView, Reviews
from config import AUTH_APP_URL, SECRET_KEY

app = FastAPI(title='client_app')

AUTH_SERVER = AsyncClient(base_url=AUTH_APP_URL)


async def _user(request: Request):
    path = request.url.path[5:]
    url = httpx.URL(path=path, query=request.url.query.encode("utf-8"))
    rp_req = AUTH_SERVER.build_request(
        request.method, url, headers=request.headers.raw,
        content=await request.body()
    )
    rp_req.headers['secret-key'] = SECRET_KEY
    rp_resp = await AUTH_SERVER.send(rp_req, stream=True)
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )

app.add_route('/user/{path:path}', _user, ['GET', 'POST', 'PUT', 'DELETE'])


@app.post('/add/user')
async def add_user(user: User,
                   request: Request,
                   db_session: AsyncSession = Depends(get_async_session)
                   ):
    print(user.dict())
    if SECRET_KEY == request.headers['secret-key']:
        await user.add_user(db_session)


@app.get('/api/reviews/{dress_id:int}')
async def get_reviews(dress_id: int,
                      page: int = 1,
                      db_session: AsyncSession = Depends(get_async_session)):
    cache = await redis_check(prefix='review', dress_id=dress_id, page=page)
    if cache:
        return JSONResponse(json.loads(cache), status_code=200)
    reviews = Reviews.parse_obj({'dress_id': dress_id, 'page': page})
    result = await reviews.from_db(db_session)
    if result:
        await redis_cache(json.dumps(result), 300, prefix='detail', id=dress_id)
        return JSONResponse(result, status_code=200)
    return JSONResponse({'error': 'not found'}, status_code=404)


@app.get('/api/dress/{dress_id:int}')
async def get_dress(dress_id: int, db_session: AsyncSession = Depends(get_async_session)):
    cache = await redis_check(prefix='detail', id=dress_id)
    if cache:
        return JSONResponse(json.loads(cache), status_code=200)
    detail_view = DetailView.parse_obj({'dress': {'id': dress_id}})
    result = await detail_view.from_db(db_session)
    if result:
        await redis_cache(json.dumps(result), 1800, prefix='detail', id=dress_id)
        return JSONResponse(result, status_code=200)
    return JSONResponse({'error': 'not found'}, status_code=404)


@app.get('/api/dress')
async def get_page(page: str = 1,
                   cat: str = None,
                   db_session: AsyncSession = Depends(get_async_session)):
    cache = await redis_check(page=page, cat=cat)
    if cache:
        return JSONResponse(json.loads(cache), status_code=200)
    category = None
    if cat:
        category = Category.parse_obj({'name': cat})
    list_view = ListView.parse_obj({'page': page,
                                    'category': category})
    result = await list_view.from_db(db_session)
    await redis_cache(json.dumps(result), 3600, page=page, cat=cat)
    if result:
        return JSONResponse(result,
                            status_code=200)
    return JSONResponse({'error': 'not found'}, status_code=404)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8001)
