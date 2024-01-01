import base64
import json
import sqlite3

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

DATABASE_FILE = "public_keys.db"

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

def delete_public_key(client_id: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM public_keys WHERE client_id=?', (client_id,))
    conn.commit()
    lastrowid = cursor.lastrowid
    conn.close()

    return lastrowid

def get_public_key(email: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT client_id, fingerprint, public_key FROM public_keys WHERE email=?', (email,))
    row = cursor.fetchone()

    conn.close()

    return {} if not row else {'client_id':row[0], 'fingerprint': json.loads(row[1]), 'public_key': row[2], 'email': email}

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
