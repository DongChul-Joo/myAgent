import bcrypt

class BCryptPasswordEncoder:
    @staticmethod
    def encode(password: str) -> str:
        # 비밀번호를 바이트로 변환
        password_bytes = password.encode('utf-8')
        # 솔트 생성 및 비밀번호 해시화
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        # 해시된 비밀번호를 문자열로 반환
        return hashed_password.decode('utf-8')

    @staticmethod
    def matches(raw_password: str, encoded_password: str) -> bool:
        # 입력된 비밀번호와 해시된 비밀번호를 바이트로 변환
        raw_password_bytes = raw_password.encode('utf-8')
        encoded_password_bytes = encoded_password.encode('utf-8')
        # 비밀번호가 일치하는지 확인
        return bcrypt.checkpw(raw_password_bytes, encoded_password_bytes)