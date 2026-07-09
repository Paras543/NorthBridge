"""
Central app settings, loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # pyrefly: ignore [unexpected-keyword]
    model_config = ConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str

    GROQ_API_KEY: str = ""
    HUGGINGFACE_API_TOKEN: str = ""

    CLERK_JWKS_URL: str = "https://topical-mastodon-81.clerk.accounts.dev/.well-known/jwks.json"
    CLERK_ISSUER: str = "https://topical-mastodon-81.clerk.accounts.dev"
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_SECRET_KEY: str = ""


settings = Settings()
