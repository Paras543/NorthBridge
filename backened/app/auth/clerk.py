import time
import httpx
import jwt
from jwt.algorithms import RSAAlgorithm
from fastapi import HTTPException, status

from app.config import settings

_jwks_cache: list = []
_jwks_cached_at: float = 0.0
_JWKS_TTL = 3600


def _get_jwks() -> list:
    global _jwks_cache, _jwks_cached_at
    now = time.time()
    if not _jwks_cache or (now - _jwks_cached_at) > _JWKS_TTL:
        try:
            response = httpx.get(settings.CLERK_JWKS_URL, timeout=10)
            response.raise_for_status()
            _jwks_cache = response.json().get("keys", [])
            _jwks_cached_at = now
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Could not fetch auth public keys: {exc}",
            )
    return _jwks_cache


def verify_token(token: str) -> dict:
    try:
        header = jwt.get_unverified_header(token)
    except jwt.exceptions.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )

    kid = header.get("kid")
    keys = _get_jwks()
    key_data = next((k for k in keys if k.get("kid") == kid), None)

    if key_data is None:
        _jwks_cache.clear()
        keys = _get_jwks()
        key_data = next((k for k in keys if k.get("kid") == kid), None)

    if key_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token signing key not found",
        )

    try:
        public_key = RSAAlgorithm.from_jwk(key_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not load signing key",
        )

    decode_options: dict = {"verify_aud": False}
    decode_kwargs: dict = {
        "algorithms": ["RS256"],
        "options": decode_options,
    }
    if settings.CLERK_ISSUER:
        decode_kwargs["issuer"] = settings.CLERK_ISSUER

    try:
        payload = jwt.decode(token, public_key, **decode_kwargs)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token issuer is invalid",
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        )

    return payload
