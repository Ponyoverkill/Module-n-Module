import json
import httpx

#from client_app import AUTH_SERVER
from starlette.requests import Request

from client_app.client_app import AUTH_SERVER
from config import SECRET_KEY


async def check_user(request: Request, token, need_permissions):
    path = 'auth'
    url = httpx.URL(path=path)
    rp_req = AUTH_SERVER.build_request(
        'POST', url,
        content=json.dumps({'token': token})
    )
    rp_req.headers['secret-key'] = SECRET_KEY
    rp_resp = await AUTH_SERVER.send(rp_req, stream=True)
    resp = rp_resp.json()
    if 'permissions' in resp.keys():
        return resp['permissions']
    return False

