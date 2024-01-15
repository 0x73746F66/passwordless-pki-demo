import base64
import binascii
import json
import sqlite3

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

DATABASE_FILE = "public_keys.db"

def save_public_key_to_db(client_id: str, fingerprint:str, public_key: str, unique_id: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS public_keys (
            client_id TEXT PRIMARY KEY,
            fingerprint TEXT NOT NULL,
            public_key TEXT NOT NULL,
            unique_id TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        INSERT INTO public_keys (client_id, fingerprint, public_key, unique_id) VALUES (?, ?, ?, ?)
        ON CONFLICT(client_id) DO UPDATE SET public_key=excluded.public_key, fingerprint=excluded.fingerprint, unique_id=excluded.unique_id;
    ''', (client_id, fingerprint, public_key, unique_id))

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

def get_public_key(unique_id: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT client_id, fingerprint, public_key FROM public_keys WHERE unique_id=?', (unique_id,))
    row = cursor.fetchone()

    conn.close()

    return {'client_id':row[0], 'fingerprint': json.loads(row[1]), 'public_key': row[2], 'unique_id': unique_id} if row else {}

def get_all_public_keys():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT client_id, fingerprint, public_key, unique_id FROM public_keys')
    rows = cursor.fetchall()

    conn.close()

    return [{'client_id':row[0], 'fingerprint': json.loads(row[1]), 'public_key': row[2], 'unique_id': row[3]} for row in rows]

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

def verify_signature(public_key, signature: str, message: str):
    try:
        public_key.verify(
            binascii.unhexlify(signature),
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=32
            ),
            hashes.SHA512()
        )
        return True
    except InvalidSignature:
        return False

def extract_authz(header_value):
    try:
        # Splitting the header value into components
        parts = header_value.split()

        if len(parts) != 4 or parts[0] != "Digest":
            return None, None, None
        # Extracting the sig, ts, and id values
        sig = parts[1].split('=')[1].strip('"')
        ts = parts[2].split('=')[1].strip('"')
        uid = parts[3].split('=')[1].strip('"')
        return sig, ts, uid
    except Exception:
        return None, None, None
