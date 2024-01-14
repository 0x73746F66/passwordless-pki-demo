from pydantic import BaseModel


class Fingerprint(BaseModel):
    canvasHash: str
    deviceMemory: str | int
    hardwareConcurrency: int
    lang: str
    platform: str
    tz: int
    ua: str
    webGLHash: str

class EncryptRequest(BaseModel):
    message: str

class RevokeKeyRequest(BaseModel):
    client_id: str

class PublicKeyRequest(BaseModel):
    unique_id: str
    public_key: str

class RegisterData(BaseModel):
    client_id: str
    public_key: str
    fingerprint: Fingerprint
    unique_id: str
