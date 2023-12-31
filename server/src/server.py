import logging
from secrets import compare_digest

import models
import utils
from cryptography.hazmat.primitives import serialization
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()
BASIC_AUTH_USER = b'demo'
BASIC_AUTH_PASSWD = b'D7lBs4uV#ngRg8hq5$'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],  # Allows all headers
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.get("/")
async def list_keys(credentials: HTTPBasicCredentials = Depends(security)):
    if not all([compare_digest(credentials.username.encode('utf8'), BASIC_AUTH_USER), compare_digest(credentials.password.encode('utf8'), BASIC_AUTH_PASSWD)]):
        return JSONResponse(content=None, status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})

    return {"records": utils.get_all_public_keys()}

@app.post("/check-key")
async def check_key(request: models.PublicKeyRequest):
    data = utils.get_public_key(request.unique_id)
    return {"exists": data.get('public_key') == request.public_key}

@app.post("/encrypt-message")
async def encrypt_message(request: models.EncryptRequest):
    data = utils.get_public_key(request.unique_id)
    public_key = serialization.load_pem_public_key(
        data['public_key'].encode(),
    )
    encrypted_message = utils.encrypt_with_public_key(request.message, public_key)
    return {"encrypted_message": encrypted_message}

@app.post("/register")
async def register(request: models.RegisterData):
    utils.save_public_key_to_db(request.client_id, request.fingerprint.json(), request.public_key, request.unique_id)
    return {"message": "Registered!"}
