# My Agent Backend Database

## 1. DB 구성

- Maria DB 10.8.x - [MariaDB](https://mariadb.org/)
- Docker Container 환경으로 구성

## 2. 설치 방법

### 1. Docker Compose 설정 확인

- `docker-compose-maria.yml` 파일에서 DB 데이터를 저장할 볼륨 정보 확인 및 수정

```yml
volumes:
  - ./mariadb:/var/lib/mysql
```

### 2. Docker Container 기동

```shell
docker-compose up -d
```

### 3. 정상 기동 확인

```shell
docker ps -a
# 혹은
docker stats
# 상태 확인 후 컨테이너 ID 복사
```

## 4. DB 초기화 확인

```shell
# 컨테이너 내부 접속
docker exec -it {컨테이너 ID} bash
# MariaDB 콘솔 접속
mysql -u root -p
# MariaDB root 계정 비밀번호 입력
MYSQL_ROOT_PASSWORD 값 입력 후 엔터
# 사용 DB 설정
use prompt;
# 테이블 목록 조회
show tables;
# 기본 입력 내용 확인
# 관리자 계정 정보
select * from aa_user;
```
