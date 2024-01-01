import logging

import models
import utils
from cryptography.hazmat.primitives import serialization
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()
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

@app.get("/list-keys")
async def list_keys():
    return {"records": utils.get_all_public_keys()}

@app.post("/check-key")
async def check_key(request: models.PublicKeyRequest):
    data = utils.get_public_key(request.unique_id)
    return {"exists": data.get('public_key') == request.public_key}

@app.post("/revoke-key")
async def revoke_key(request: models.RevokeKeyRequest):
    return {"result": utils.delete_public_key(request.client_id)}

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
