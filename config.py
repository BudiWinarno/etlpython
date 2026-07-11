import os

class Config:

    SECRET_KEY = "123456789"

    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "latihanpentaho"

    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    UPLOAD_FOLDER = "uploads"

    OUTPUT_FOLDER = "output"

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024