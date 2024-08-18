from pydantic import BaseSettings

class CommonEnvs(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_TIME: int
    REFRESH_TOKEN_EXPIRE_TIME: int
    DATABASE_URL: str
    DEVICE:str
    OPENAI_API_KEY:str

    class Config:
        case_sensitive = False  # 대소문자 구분 없이 불러옴

commonEnvs = CommonEnvs()