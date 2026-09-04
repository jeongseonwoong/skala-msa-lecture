package com.lecture.auth.model;

import jakarta.persistence.*;
import lombok.*;

/**
 * auth-server 의 User 엔티티 — 부분 재구성본.
 *
 * auth-server(msa-lecture/auth-server:1.0)는 소스가 배포되지 않는 사전 빌드 이미지다.
 * 이미지 안 enum 은 STUDENT/INSTRUCTOR 만 알고 있어, 신 도메인 시드(MD/SELLER/BUYER)로
 * 로그인하면 Hibernate 가 "No enum constant ...Role.MD" 로 실패한다.
 *
 * 이 파일은 이미지의 User 클래스 형태(javap 로 확인)를 그대로 복원하고 Role enum 에
 * MD/SELLER/BUYER 를 추가한 것이다. scripts/build-local.sh 가 이미지의 BOOT-INF/lib 를
 * 클래스패스로 삼아 이 파일만 재컴파일하고, app.jar 안의
 * BOOT-INF/classes/.../User*.class 3개만 교체한다 (나머지 클래스는 원본 유지).
 *
 * 즉 auth-server 전체 소스가 아니라, enum 패치를 재현 가능하게 만들기 위한 최소 파일이다.
 */
@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private String name;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role;

    public enum Role {
        // 신 도메인 (이커머스 상품 이슈 모니터링)
        MD,
        SELLER,
        BUYER,
        // 구 도메인 — 이미지 안 DataInitializer 가 참조하므로 유지
        STUDENT,
        INSTRUCTOR
    }
}
