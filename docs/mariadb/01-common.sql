CREATE DATABASE my_agent;

CREATE USER 'my_agent'@'%' IDENTIFIED BY 'my_agent@pwd';

GRANT SELECT, INSERT, UPDATE, DELETE ON my_agent.* TO 'my_agent'@'%';
GRANT TRIGGER ON my_agent.* TO 'my_agent'@'%';
FLUSH PRIVILEGES;

USE my_agent;

CREATE TABLE `0000_user` (
    `email` VARCHAR(100) NOT NULL COMMENT '이메일',
    `created_at` DATETIME(6) NOT NULL DEFAULT now() COMMENT '등록일시',
    `created_by` VARCHAR(36) NOT NULL COMMENT '등록 사용자 계정',
    `created_by_name` VARCHAR(50) NOT NULL COMMENT '등록자 이름',
    `updated_at` DATETIME(6) NOT NULL DEFAULT now() COMMENT '수정일시',
    `updated_by` VARCHAR(36) NOT NULL COMMENT '수정 사용자 계정',
    `updated_by_name` VARCHAR(50) NOT NULL COMMENT '수정자 이름',
    `deleted` VARCHAR(1) NOT NULL DEFAULT 'N' COMMENT '삭제 여부',
    `last_login_timestamp` DATETIME(6) DEFAULT NULL COMMENT '마지막 로그인 일시',
    `layout_type` VARCHAR(10) NOT NULL COMMENT '레이아웃 타입',
    `password` VARCHAR(100) NOT NULL COMMENT '사용자 비밀번호',
    `user_name` VARCHAR(50) NOT NULL COMMENT '사용자 이름',
    `user_role_type` VARCHAR(20) NOT NULL COMMENT '사용자 권한',
    `uuid` VARCHAR(36) NOT NULL COMMENT '사용자 UUID',
    PRIMARY KEY (`email`)
) COMMENT = '사용자'
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4;

CREATE TABLE `0100_session` (
    `email` VARCHAR(100) NOT NULL COMMENT '이메일',
    `created_at` DATETIME(6) NOT NULL DEFAULT now() COMMENT 'Refresh 토큰 생성일시',
    `expired_at` DATETIME(6) NOT NULL COMMENT 'Refresh 토큰 만료일시',
    `refresh_token` VARCHAR(10000) NOT NULL COMMENT 'Refresh 토큰',
    `remote_ip` VARCHAR(36) NOT NULL COMMENT '접속 IP(IPv4)',
    PRIMARY KEY (`remote_ip`)
) COMMENT = 'JWT_Refresh_token 관리'
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4;

-- admin@myagent.com / chatbot@myagent
INSERT INTO
  0000_user (
    email,
    created_by,
    updated_by,
    deleted,
    last_login_timestamp,
    layout_type,
    password,
    user_name,
    user_role_type,
    `uuid`,
    created_by_name,
    updated_by_name
  )
VALUES
  (
    'admin@myagent.com',
    'system',
    'system',
    'N',
    NULL,
    'LAYOUT_1',
    '$2b$12$HnoQUOyf8acagft1.aCYCeB.3xqfHassmfi6wh.nPhhoLoqxgqQEa',
    '관리자',
    'ROLE_ADMIN',
    uuid(),
    'System Admin',
    'System Admin'
  );
