-- 이커머스 셀러 운영 평가 솔루션 초기 DDL
-- Spring JPA ddl-auto: update 로도 생성되지만
-- 명시적 DDL로 테이블 선후 관계를 문서화
--
-- 물리 테이블명은 기존(users/courses/enrollments/payments)을 유지한다.
-- 서비스 코드 영향을 최소화하고 도메인 의미만 재정의:
--   courses      = 상품(product)          instructor_id = 셀러 ID
--   enrollments  = 주문(order)            user_id       = 구매자 ID
--   payments     = 결제/정산(settlement)

-- 회원: MD(솔루션 운영자) / SELLER(평가 대상) / BUYER(주문 발생 소비자)
CREATE TABLE IF NOT EXISTS users (
    id            BIGINT       NOT NULL AUTO_INCREMENT,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password      VARCHAR(255) NOT NULL,
    name          VARCHAR(100) NOT NULL,
    role          VARCHAR(20)  NOT NULL COMMENT 'MD | SELLER | BUYER',
    seller_status VARCHAR(20)  NULL     COMMENT 'ACTIVE | WARNING | TERMINATED (SELLER 전용)',
    created_at    DATETIME(6),
    updated_at    DATETIME(6),
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 셀러가 상품 등록 (instructor_id → users.id, 셀러 ID 의미)
CREATE TABLE IF NOT EXISTS courses (
    id               BIGINT        NOT NULL AUTO_INCREMENT,
    title            VARCHAR(255)  NOT NULL,
    description      TEXT,
    category         VARCHAR(50)   NOT NULL COMMENT 'FASHION|BEAUTY|FOOD|DIGITAL|HOME|SPORTS|BOOK|OTHER',
    price            DECIMAL(10,2) NOT NULL,
    instructor_id    BIGINT        NOT NULL COMMENT '셀러 ID (users.id)',
    enrollment_count INT           NOT NULL DEFAULT 0 COMMENT '누적 판매건수',
    status           VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE | INACTIVE (판매중 | 판매중지)',
    created_at       DATETIME(6),
    updated_at       DATETIME(6),
    PRIMARY KEY (id),
    FOREIGN KEY (instructor_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 구매자가 주문 생성 (user_id → 구매자, course_id → 상품)
-- 셀러 평가의 핵심 지표 소스(판매량·취소율). 한 구매자가 같은 상품을 여러 번 주문 가능하므로 유니크 제약 없음
CREATE TABLE IF NOT EXISTS enrollments (
    id          BIGINT      NOT NULL AUTO_INCREMENT,
    user_id     BIGINT      NOT NULL COMMENT '구매자 ID (users.id)',
    course_id   BIGINT      NOT NULL COMMENT '상품 ID (courses.id)',
    status      VARCHAR(20) NOT NULL DEFAULT 'COMPLETED' COMMENT 'COMPLETED | CANCELLED | RETURNED',
    created_at  DATETIME(6),
    updated_at  DATETIME(6),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id)   REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 주문 결제·정산 (user_id → 구매자, course_id → 상품)
CREATE TABLE IF NOT EXISTS payments (
    id              BIGINT        NOT NULL AUTO_INCREMENT,
    user_id         BIGINT        NOT NULL,
    course_id       BIGINT        NOT NULL,
    amount          DECIMAL(10,2) NOT NULL COMMENT '매출액 (환불 시 환불금액 기준)',
    status          VARCHAR(20)   NOT NULL DEFAULT 'COMPLETED' COMMENT 'COMPLETED | REFUNDED | FAILED | CANCELLED',
    transaction_id  VARCHAR(255)  UNIQUE,
    created_at      DATETIME(6),
    updated_at      DATETIME(6),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id)   REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
