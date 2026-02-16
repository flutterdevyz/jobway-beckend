from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Jobway"
    # Basic SQLite for dev, can be swapped for PostgreSQL
    DATABASE_URL: str = "sqlite:///./jobway_v3.db"
    SECRET_KEY: str = "supersecretkey" # Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
