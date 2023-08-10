from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CLIENT_ID: str
    CLIENT_SECRET: SecretStr
    class Config:
        env_file = 'keycloak.env'
        env_file_encoding = 'ascii'


settings = Settings()
