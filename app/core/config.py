# app/core/config.py
import os
from dotenv import load_dotenv

# as config is not where main.py, so we have to declaer the path
from pathlib import Path

env_path = Path(".") / ".env"
# print(env_path)
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_TITLE: str = "Global Source Export Apis"
    PROJECT_VERSION: str = "0.1.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120


class S3Config:
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN")


settings = Settings()
s3_config = S3Config()
