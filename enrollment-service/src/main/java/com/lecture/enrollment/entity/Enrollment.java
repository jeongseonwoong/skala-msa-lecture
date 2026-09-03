package com.lecture.enrollment.entity;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
// 주문 도메인: 한 구매자가 같은 상품을 여러 번 주문할 수 있으므로 (user_id, course_id) 유니크 제약 없음
@Table(name = "enrollments")
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EntityListeners(AuditingEntityListener.class)
public class Enrollment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "course_id", nullable = false)
    private Long courseId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private Status status = Status.PENDING;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    public enum Status {
        PENDING,    // 주문 생성, 결제 대기
        COMPLETED,  // 결제 완료된 정상 주문
        CANCELLED,  // 취소
        RETURNED    // 반품
    }

    public void complete() {
        this.status = Status.COMPLETED;
    }

    public void cancel() {
        this.status = Status.CANCELLED;
    }
}
