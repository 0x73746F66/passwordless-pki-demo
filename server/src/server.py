import base64
import json
import logging
import sqlite3

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

DATABASE_FILE = "public_keys.db"
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

class Fingerprint(BaseModel):
    canvasHash: str
    deviceMemory: str
    hardwareConcurrency: int
    lang: str
    platform: str
    tz: int
    ua: str
    webGLHash: str

class EncryptRequest(BaseModel):
    unique_id: str
    message: str

class PublicKeyRequest(BaseModel):
    unique_id: str
    public_key: str

class RegisterData(BaseModel):
    client_id: str
    public_key: str
    fingerprint: Fingerprint
    unique_id: str

@app.get("/")
async def list_keys():
    keys = get_all_public_keys()
    return {"records": keys}

@app.post("/check-key")
async def check_key(request: PublicKeyRequest):
    data = get_public_key(request.unique_id)
    return {"exists": data.public_key == request.public_key}

@app.post("/encrypt-message")
async def encrypt_message(request: EncryptRequest):
    data = get_public_key(request.unique_id)
    public_key = serialization.load_pem_public_key(
        data['public_key'].encode(),
    )
    encrypted_message = encrypt_with_public_key(request.message, public_key)
    return {"encrypted_message": encrypted_message}

@app.post("/register")
async def register(request: RegisterData):
    save_public_key_to_db(request.client_id, request.fingerprint.json(), request.public_key, request.unique_id)
    return {"message": "Registered!"}

def save_public_key_to_db(client_id: str, fingerprint:str, public_key: str, email: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS public_keys (
            client_id TEXT PRIMARY KEY,
            fingerprint TEXT NOT NULL,
            public_key TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        INSERT INTO public_keys (client_id, fingerprint, public_key, email) VALUES (?, ?, ?, ?)
        ON CONFLICT(client_id) DO UPDATE SET public_key=excluded.public_key, fingerprint=excluded.fingerprint, email=excluded.email;
    ''', (client_id, fingerprint, public_key, email))

    conn.commit()
    conn.close()

def get_public_key(email: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT client_id, fingerprint, public_key FROM public_keys WHERE email=?', email)
    row = cursor.fetchone()

    conn.close()

    return {'client_id':row[0], 'fingerprint': json.loads(row[1]), 'public_key': row[2], 'email': email}

def get_all_public_keys():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT client_id, fingerprint, public_key, email FROM public_keys')
    rows = cursor.fetchall()

    conn.close()

    return [{'client_id':row[0], 'fingerprint': json.loads(row[1]), 'public_key': row[2], 'email': row[3]} for row in rows]

def encrypt_with_public_key(message: str, public_key) -> str:
    encrypted = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA512()),
            algorithm=hashes.SHA512(),
            label=None
        )
    )
    # Encode the encrypted message with base64 for safe transport
    return base64.b64encode(encrypted).decode()
