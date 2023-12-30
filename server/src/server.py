import json
import logging
import sqlite3

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

class PublicKeyEntry(BaseModel):
    client_id: str
    public_key: str
    fingerprint: Fingerprint
    email: str | None

@app.get("/")
async def list_keys():
    keys = get_all_public_keys()
    return {"records": keys}

@app.post("/submit-key")
async def submit_key(entry: PublicKeyEntry):
    save_public_key_to_db(entry.client_id, entry.fingerprint.json(), entry.public_key)
    return {"message": "Public key saved successfully"}

def save_public_key_to_db(client_id: str, fingerprint:str, public_key: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS public_keys (
            client_id TEXT PRIMARY KEY,
            fingerprint TEXT NOT NULL,
            public_key TEXT NOT NULL,
            email TEXT DEFAULT NULL
        )
    ''')

    cursor.execute('''
        INSERT INTO public_keys (client_id, fingerprint, public_key) VALUES (?, ?, ?)
        ON CONFLICT(client_id) DO UPDATE SET public_key=excluded.public_key, fingerprint=excluded.fingerprint;
    ''', (client_id, fingerprint, public_key))

    conn.commit()
    conn.close()

def get_all_public_keys():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT client_id, fingerprint, public_key, email FROM public_keys')
    rows = cursor.fetchall()

    conn.close()

    return [{'client_id':row[0], 'fingerprint': json.loads(row[1]), 'public_key': row[2], 'email': row[3]} for row in rows]
