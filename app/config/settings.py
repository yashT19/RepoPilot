import os

from pydantic_settings import (
BaseSettings,
SettingsConfigDict,
)

class Settings(BaseSettings):
  APP_NAME: str

  API_V1_PREFIX: str

  HOST: str

  PORT: int

  DATABASE_URL: str

  GROQ_API_KEY: str

  GROQ_MODEL: str

  STORAGE_ROOT: str

  LANGSMITH_TRACING: bool

  LANGSMITH_API_KEY: str

  LANGSMITH_PROJECT: str

  model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore",
)
settings = Settings()

# --------------------------------------------------

# Configure LangSmith environment variables

# --------------------------------------------------

os.environ["LANGSMITH_TRACING"] = str(
settings.LANGSMITH_TRACING
).lower()

os.environ["LANGSMITH_API_KEY"] = (
settings.LANGSMITH_API_KEY
)

os.environ["LANGSMITH_PROJECT"] = (
settings.LANGSMITH_PROJECT
)

os.environ["LANGSMITH_ENDPOINT"] = (
"https://api.smith.langchain.com"
)
