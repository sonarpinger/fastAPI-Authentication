import uvicorn
import logging

from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
app = FastAPI()

from starlette.config import Config
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError

logger = logging.getLogger(__name__)

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')

templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

app.add_middleware(SessionMiddleware, secret_key='!secret')

# config = Config('google.env')
# oauth = OAuth(config)

# # Google
# CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
# oauth.register(
#     name='google',
#     server_metadata_url=CONF_URL,
#     client_kwargs={
#         'scope': 'openid profile email',
#     }
# )

from config import settings

oauth = OAuth()

# Keycloak
CONF_URL = 'https://idp.nevada.dev/realms/NSHE/.well-known/openid-configuration'


oauth.register(
    name='keycloak',
    client_id=settings.CLIENT_ID,
    cliend_secret=settings.CLIENT_SECRET,
    server_metadata_url=CONF_URL,
    redirect_uri='http://127.0.0.1:8000/auth',
        client_kwargs={
        'scope': 'openid profile email',
    }
)

@app.route('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.keycloak.authorize_redirect(request, redirect_uri)

@app.route('/auth')
async def auth(request: Request):
    try:
        token = await oauth.keycloak.authorize_access_token(request)
    except OAuthError as error:
        return templates.TemplateResponse('error.html', {'request': request, 'error': error.error})
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/success')

@app.get('/success')
async def private(request: Request):
    user = request.session.get('user')
    if user:
        return templates.TemplateResponse('success.html', {'request': request, 'user': user})
    else:
        return RedirectResponse(url='/error')

@app.get('/error')
async def error():
    return {'result': 'This is a error endpoint.'}

@app.get('/')
async def public(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000)
