package com.lecture.user.entity;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EntityListeners(AuditingEntityListener.class)
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

    // 셀러 운영 상태 (SELLER 역할만 값 존재, MD/BUYER는 null)
    @Enumerated(EnumType.STRING)
    @Column(name = "seller_status")
    private SellerStatus sellerStatus;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    public enum Role {
        MD,       // 솔루션 운영자(카테고리 MD) - 우리 서비스 로그인 유저
        SELLER,   // 평가 대상 셀러
        BUYER     // 주문을 발생시키는 소비자(데이터 소스)
    }

    public enum SellerStatus {
        ACTIVE,       // 정상 입점 유지
        WARNING,      // 경고
        TERMINATED    // 퇴출
    }
}
