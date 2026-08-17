from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, jwk
from jose.utils import long_to_base64
import json
import httpx
from functools import lru_cache

from backend.config import SUPABASE_JWT_SECRET, SUPABASE_URL

security = HTTPBearer()

_jwks_cache = None


async def _get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json", timeout=5)
                _jwks_cache = resp.json()
        except Exception:
            _jwks_cache = {"keys": []}
    return _jwks_cache


def _decode_hs256(token: str) -> dict:
    return jwt.decode(
        token,
        SUPABASE_JWT_SECRET,
        algorithms=["HS256"],
        audience="authenticated",
    )


async def _decode_es256(token: str) -> dict:
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")

    jwks = await _get_jwks()
    for key_data in jwks.get("keys", []):
        if key_data.get("kid") == kid:
            public_key = jwk.construct(key_data)
            return jwt.decode(
                token,
                public_key,
                algorithms=["ES256"],
                audience="authenticated",
            )
    raise JWTError("Key not found in JWKS")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "")

        if alg == "ES256":
            payload = await _decode_es256(token)
        else:
            payload = _decode_hs256(token)

        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
