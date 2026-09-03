-- 이커머스 셀러 운영 평가 솔루션 시드 데이터
-- Sprint 1 데모용. 이슈 규칙(LOW_SALES / SALES_DECLINING / HIGH_CANCEL_RATE /
-- HIGH_REFUND_RATE / LOW_REVENUE / NO_RECENT_ORDER)이 실제로 트리거되도록
-- 셀러를 3개 그룹(우수 / 주의 / 퇴출검토)으로 나눠 최근 60일 주문·결제를 생성한다.
--
-- 계정 비밀번호는 전부 'password123' (BCrypt)

SET @pw := '$2y$10$Cu7Q/tjKffT9tmtFsGpphuyY2qDtpNxn9wwJQ7zJeNRaP84Ma8Eoe';

-- ── 회원 ────────────────────────────────────────────────────────────────
-- id 1        : MD (솔루션 로그인 유저)
-- id 2 ~ 11   : 구매자 10명 (주문 발생 소스)
-- id 12 ~ 23  : 셀러 12명 (평가 대상, 최초 seller_status = ACTIVE)
INSERT INTO users (id, email, password, name, role, seller_status, created_at, updated_at) VALUES
 (1,  'md@example.com',      @pw, 'MD 김담당',       'MD',     NULL,     NOW(), NOW()),
 (2,  'buyer01@example.com', @pw, '구매자01',        'BUYER',  NULL,     NOW(), NOW()),
 (3,  'buyer02@example.com', @pw, '구매자02',        'BUYER',  NULL,     NOW(), NOW()),
 (4,  'buyer03@example.com', @pw, '구매자03',        'BUYER',  NULL,     NOW(), NOW()),
 (5,  'buyer04@example.com', @pw, '구매자04',        'BUYER',  NULL,     NOW(), NOW()),
 (6,  'buyer05@example.com', @pw, '구매자05',        'BUYER',  NULL,     NOW(), NOW()),
 (7,  'buyer06@example.com', @pw, '구매자06',        'BUYER',  NULL,     NOW(), NOW()),
 (8,  'buyer07@example.com', @pw, '구매자07',        'BUYER',  NULL,     NOW(), NOW()),
 (9,  'buyer08@example.com', @pw, '구매자08',        'BUYER',  NULL,     NOW(), NOW()),
 (10, 'buyer09@example.com', @pw, '구매자09',        'BUYER',  NULL,     NOW(), NOW()),
 (11, 'buyer10@example.com', @pw, '구매자10',        'BUYER',  NULL,     NOW(), NOW()),
 (12, 'seller01@example.com', @pw, '셀러01 (우수)',      'SELLER', 'ACTIVE', NOW(), NOW()),
 (13, 'seller02@example.com', @pw, '셀러02 (우수)',      'SELLER', 'ACTIVE', NOW(), NOW()),
 (14, 'seller03@example.com', @pw, '셀러03 (우수)',      'SELLER', 'ACTIVE', NOW(), NOW()),
 (15, 'seller04@example.com', @pw, '셀러04 (우수)',      'SELLER', 'ACTIVE', NOW(), NOW()),
 (16, 'seller05@example.com', @pw, '셀러05 (주의)',      'SELLER', 'ACTIVE', NOW(), NOW()),
 (17, 'seller06@example.com', @pw, '셀러06 (주의)',      'SELLER', 'ACTIVE', NOW(), NOW()),
 (18, 'seller07@example.com', @pw, '셀러07 (주의)',      'SELLER', 'ACTIVE', NOW(), NOW()),
 (19, 'seller08@example.com', @pw, '셀러08 (주의)',      'SELLER', 'ACTIVE', NOW(), NOW()),
 (20, 'seller09@example.com', @pw, '셀러09 (퇴출검토)',  'SELLER', 'ACTIVE', NOW(), NOW()),
 (21, 'seller10@example.com', @pw, '셀러10 (퇴출검토)',  'SELLER', 'ACTIVE', NOW(), NOW()),
 (22, 'seller11@example.com', @pw, '셀러11 (퇴출검토)',  'SELLER', 'ACTIVE', NOW(), NOW()),
 (23, 'seller12@example.com', @pw, '셀러12 (퇴출검토)',  'SELLER', 'ACTIVE', NOW(), NOW());

-- ── 상품 + 주문 + 결제 생성 ─────────────────────────────────────────────
DELIMITER $$
CREATE PROCEDURE seed_ecommerce()
BEGIN
    DECLARE si         INT DEFAULT 0;      -- 셀러 인덱스 0..11
    DECLARE pj         INT;                -- 셀러별 상품 인덱스 0..2
    DECLARE seller_id  BIGINT;
    DECLARE prod_id    BIGINT;
    DECLARE grp        INT;                -- 0=우수 1=주의 2=퇴출검토
    DECLARE cat        VARCHAR(20);
    DECLARE base_price DECIMAL(10,2);
    DECLARE n_orders   INT;
    DECLARE k          INT;
    DECLARE day_off    INT;
    DECLARE buyer_id   BIGINT;
    DECLARE r          DOUBLE;             -- 주문 상태 추첨
    DECLARE d          DOUBLE;             -- 주문 발생일 버킷 추첨
    DECLARE o_status   VARCHAR(20);
    DECLARE p_status   VARCHAR(20);
    DECLARE ts         DATETIME(6);

    WHILE si < 12 DO
        SET seller_id = 12 + si;
        SET grp = CASE WHEN si < 4 THEN 0 WHEN si < 8 THEN 1 ELSE 2 END;

        SET pj = 0;
        WHILE pj < 3 DO
            SET prod_id    = si * 3 + pj + 1;
            SET cat        = ELT(1 + MOD(prod_id, 8),
                                 'FASHION','BEAUTY','FOOD','DIGITAL','HOME','SPORTS','BOOK','OTHER');
            SET base_price = 9900 + MOD(prod_id * 37, 40) * 1000;   -- 9,900 ~ 48,900

            INSERT INTO courses (id, title, description, category, price,
                                 instructor_id, enrollment_count, status, created_at, updated_at)
            VALUES (prod_id,
                    CONCAT(cat, ' 상품 #', prod_id),
                    CONCAT('셀러 ', seller_id, ' 의 ', cat, ' 카테고리 상품'),
                    cat, base_price, seller_id, 0, 'ACTIVE',
                    NOW() - INTERVAL 90 DAY, NOW() - INTERVAL 90 DAY);

            -- 그룹별 주문량 (우수: 많음 / 주의: 보통 / 퇴출검토: 적음 → LOW_SALES·LOW_REVENUE 유발)
            SET n_orders = CASE grp
                             WHEN 0 THEN 70 + FLOOR(RAND() * 40)
                             WHEN 1 THEN 34 + FLOOR(RAND() * 18)
                             ELSE        10 + FLOOR(RAND() * 12)
                           END;

            SET k = 0;
            WHILE k < n_orders DO
                -- 주문 발생일: 오늘로부터 day_off 일 전
                SET d = RAND();
                IF grp = 0 THEN
                    -- 최근 60일 고르게 → 최근 주문 존재, 하락 추세 없음
                    SET day_off = FLOOR(RAND() * 60);
                ELSEIF grp = 1 THEN
                    -- 최근 7일 10% / 이전 7일 25% / 그 이전 65% → SALES_DECLINING 유발, 최근 주문은 존재
                    IF d < 0.10 THEN
                        SET day_off = FLOOR(RAND() * 7);
                    ELSEIF d < 0.35 THEN
                        SET day_off = 7 + FLOOR(RAND() * 7);
                    ELSE
                        SET day_off = 14 + FLOOR(RAND() * 46);
                    END IF;
                ELSE
                    -- 최근 15일 주문 0건 → NO_RECENT_ORDER 유발
                    SET day_off = 15 + FLOOR(RAND() * 45);
                END IF;

                SET buyer_id = 2 + FLOOR(RAND() * 10);
                SET ts = NOW() - INTERVAL day_off DAY - INTERVAL FLOOR(RAND() * 86400) SECOND;

                -- 주문 상태 분포 (취소+반품 비율이 그룹별로 다름)
                SET r = RAND();
                IF grp = 0 THEN
                    SET o_status = CASE WHEN r < 0.03 THEN 'CANCELLED'
                                        WHEN r < 0.05 THEN 'RETURNED'
                                        ELSE 'COMPLETED' END;
                ELSEIF grp = 1 THEN
                    SET o_status = CASE WHEN r < 0.11 THEN 'CANCELLED'
                                        WHEN r < 0.18 THEN 'RETURNED'
                                        ELSE 'COMPLETED' END;
                ELSE
                    SET o_status = CASE WHEN r < 0.18 THEN 'CANCELLED'
                                        WHEN r < 0.30 THEN 'RETURNED'
                                        ELSE 'COMPLETED' END;
                END IF;

                INSERT INTO enrollments (user_id, course_id, status, created_at, updated_at)
                VALUES (buyer_id, prod_id, o_status, ts, ts);

                SET p_status = CASE o_status
                                 WHEN 'CANCELLED' THEN 'CANCELLED'
                                 WHEN 'RETURNED'  THEN 'REFUNDED'
                                 ELSE 'COMPLETED' END;

                INSERT INTO payments (user_id, course_id, amount, status,
                                      transaction_id, created_at, updated_at)
                VALUES (buyer_id, prod_id, base_price, p_status,
                        CONCAT('TXN-', prod_id, '-', k), ts, ts);

                SET k = k + 1;
            END WHILE;

            SET pj = pj + 1;
        END WHILE;

        SET si = si + 1;
    END WHILE;

    -- 누적 판매건수 = 완료(COMPLETED) 주문 수
    UPDATE courses c
    SET c.enrollment_count = (
        SELECT COUNT(*) FROM enrollments e
        WHERE e.course_id = c.id AND e.status = 'COMPLETED'
    );
END$$
DELIMITER ;

CALL seed_ecommerce();
DROP PROCEDURE seed_ecommerce;
