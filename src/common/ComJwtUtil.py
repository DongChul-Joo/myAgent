from .ComEnv import commonEnvs
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jose import jwt
from jose.exceptions import JWTError
from typing import Optional, Dict

class AbstractJwtEncoder(ABC):
    """
    Jwt 인코더 추상클래스
    encode 메소드를 구현
    
    :param data: Jwt에 담을 데이터
    :param expires_delta: Jwt 만료 시간
    :param secret_key: Jwt 암호화 키
    :param algorithm: Jwt 암호화 알고리즘
    """

    @abstractmethod
    def encode(
        self, data: dict, expires_delta: int, secret_key: str, algorithm: str
    ) -> str:
        pass

class JwtEncoder(AbstractJwtEncoder):
    def encode(
        self, data: dict, expires_delta: int, secret_key: str, algorithm: str
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(ZoneInfo("Asia/Seoul")) + timedelta(minutes=expires_delta)
        to_encode.update({"exp": expire})
        return jwt.encode(claims=to_encode, key=secret_key, algorithm=algorithm)

class AbstractJwtDecoder(ABC):
    """
    Jwt 디코더 추상클래스
    decode 메소드를 구현
    
    :param token: Jwt 토큰
    :param secret_key: Jwt 암호화 키
    :param algorithm: Jwt 암호화 알고리즘
    """

    @abstractmethod
    def decode(self, token: str, secret_key: str, algorithm: str ,verify_exp=True) -> Optional[Dict]:
        pass

class JwtDecoder(AbstractJwtDecoder):
    def decode(self, token: str, secret_key: str, algorithm: str ,verify_exp=True) -> Optional[Dict]:
        try:
            return jwt.decode(token, key=secret_key, algorithms=[algorithm])
        except JWTError:
            return None

class JwtUtil:
    """
    Jwt 로그인시 access token, refresh token을 생성하는 로직
    """

    def __init__(
        self,
        access_token_expire_time: int = None,
        refresh_token_expire_time: int = None,
        algorithm: str = None,
        secret_key: str = None
    ):
        self.encoder = JwtEncoder()
        self.decoder = JwtDecoder()
        self.algorithm = algorithm or commonEnvs.ALGORITHM
        self.secret_key = secret_key or commonEnvs.SECRET_KEY
        self.access_token_expire_time = access_token_expire_time or commonEnvs.ACCESS_TOKEN_EXPIRE_TIME
        self.refresh_token_expire_time = refresh_token_expire_time or commonEnvs.REFRESH_TOKEN_EXPIRE_TIME

    def createAccessToken(self, data: dict) -> str:
        return self._createToken(data, self.access_token_expire_time)

    def createRefreshToken(self, data: dict) -> str:
        return self._createToken(data, self.refresh_token_expire_time)
    
    def createRefreshAccessToken(self, refresh_token: str) -> Optional[str]:
        """
        리프레시 토큰을 사용하여 새로운 액세스 토큰을 생성합니다.
        
        :param refresh_token: 리프레시 토큰
        :return: 새로운 액세스 토큰 또는 None
        """
        payload = self.checkTokenExpired(refresh_token)
        if payload:
            return self.createAccessToken(payload)
        return None

    def _createToken(self, data: dict, expires_delta: int) -> str:
        """
        Jwt 토큰을 생성합니다.
        
        :param data: Jwt에 담을 데이터
        :param expires_delta: Jwt 만료 시간 (분 단위)
        :return: Jwt 토큰 문자열
        """
        return self.encoder.encode(data, expires_delta, self.secret_key, self.algorithm)

    def checkTokenExpired(self, token: str) -> Optional[Dict]:
        payload = self.decoder.decode(token, self.secret_key, self.algorithm)
        now = datetime.timestamp(datetime.now(ZoneInfo("Asia/Seoul")))
        if payload and payload.get("exp", 0) < now:
            return None

        return payload
    
    def getPayload(self, token: str , verify_exp=False) -> Optional[Dict]:
        payload = self.decoder.decode(token, self.secret_key, self.algorithm , verify_exp)
        now = datetime.timestamp(datetime.now(ZoneInfo("Asia/Seoul")))
        if payload:
            return None

        return payload
