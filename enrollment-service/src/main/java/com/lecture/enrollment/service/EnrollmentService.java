package com.lecture.enrollment.service;

import com.lecture.enrollment.dto.EnrollmentDto;
import com.lecture.enrollment.entity.Enrollment;
import com.lecture.enrollment.kafka.EnrollmentKafkaProducer;
import com.lecture.enrollment.kafka.KafkaEvent;
import com.lecture.enrollment.repository.EnrollmentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class EnrollmentService {

    private final EnrollmentRepository enrollmentRepository;
    private final CourseServiceClient courseServiceClient;
    private final PaymentServiceClient paymentServiceClient;
    private final EnrollmentKafkaProducer kafkaProducer;
    private final EnrollmentWriteService enrollmentWriteService;

    /**
     * 수강신청 전체 흐름
     * 1. 강의 존재 확인
     * 2. 중복 수강 확인
     * 3. Enrollment 생성 및 즉시 커밋 (PENDING)
     * 4. 결제 요청
     */
    public EnrollmentDto.EnrollmentResponse enroll(Long userId, Long courseId) {
        if (!courseServiceClient.existsCourse(courseId)) {
            throw new IllegalArgumentException("존재하지 않는 상품입니다: " + courseId);
        }

        // 한 구매자가 같은 상품을 여러 번 주문할 수 있으므로 중복 주문 검사를 하지 않는다

        Enrollment enrollment = enrollmentWriteService.createPendingEnrollment(userId, courseId);

        paymentServiceClient.requestPayment(userId, courseId, BigDecimal.valueOf(99000));

        log.info("[EnrollmentService] 수강신청 완료 (결제 대기) - enrollmentId: {}", enrollment.getId());
        return EnrollmentDto.EnrollmentResponse.from(enrollment);
    }

    /**
     * 수강 활성화
     */
    @Transactional
    public void activateEnrollment(Long userId, Long courseId) {
        Enrollment enrollment = enrollmentRepository.findByUserIdAndCourseId(userId, courseId)
                .orElseThrow(() -> new IllegalArgumentException(
                        "수강 정보를 찾을 수 없습니다 - userId: " + userId + ", courseId: " + courseId));

        enrollment.complete();

        courseServiceClient.increaseEnrollmentCount(courseId);

        kafkaProducer.publishEnrollmentCompleted(
                KafkaEvent.EnrollmentCompletedEvent.builder()
                        .enrollmentId(enrollment.getId())
                        .userId(userId)
                        .courseId(courseId)
                        .build()
        );

        log.info("[EnrollmentService] 수강 활성화 완료 - enrollmentId: {}", enrollment.getId());
    }

    /**
     * 사용자 수강 목록 조회
     * - course-service에서 강의 상세 정보를 붙여서 반환
     */
    public List<EnrollmentDto.EnrollmentResponse> getEnrollmentsByUser(Long userId) {
        List<Enrollment> enrollments = enrollmentRepository.findByUserId(userId);

        return enrollments.stream()
                .map(enrollment -> {
                    Map<String, Object> courseInfo = courseServiceClient.getCourse(enrollment.getCourseId());

                    EnrollmentDto.CourseSummary courseSummary = EnrollmentDto.CourseSummary.builder()
                            .id(toLong(courseInfo.get("id")))
                            .title((String) courseInfo.get("title"))
                            .description((String) courseInfo.get("description"))
                            .category(normalizeCategory((String) courseInfo.get("category")))
                            .price(toInteger(courseInfo.get("price")))
                            .thumbnail((String) courseInfo.get("thumbnail"))
                            .instructorName(
                                    firstNonNull(
                                            (String) courseInfo.get("instructorName"),
                                            (String) courseInfo.get("teacherName"),
                                            (String) courseInfo.get("instructor_name")
                                    )
                            )
                            .enrollmentCount(toInteger(
                                    firstNonNullObject(
                                            courseInfo.get("enrollmentCount"),
                                            courseInfo.get("enrollment_count")
                                    )
                            ))
                            .build();

                    return EnrollmentDto.EnrollmentResponse.from(enrollment, courseSummary);
                })
                .collect(Collectors.toList());
    }

    /**
     * 수강 이력 조회 - 추천 서비스용
     */
    public EnrollmentDto.EnrollmentHistoryResponse getEnrollmentHistory(Long userId) {
        List<Long> activeCourseIds = enrollmentRepository
                .findByUserIdAndStatus(userId, Enrollment.Status.COMPLETED)
                .stream()
                .map(Enrollment::getCourseId)
                .collect(Collectors.toList());

        return EnrollmentDto.EnrollmentHistoryResponse.builder()
                .userId(userId)
                .activeCourseIds(activeCourseIds)
                .build();
    }

    /**
     * 셀러별 주문 이력 조회 - 셀러 평가 서비스용
     * 1. course-service에서 셀러(instructorId)의 상품 ID 목록을 받아온다
     * 2. 해당 상품들에 속한 모든 주문을 반환한다 (상태 무관)
     */
    public List<EnrollmentDto.SellerOrderResponse> getOrdersBySeller(Long sellerId) {
        List<Long> productIds = courseServiceClient.getProductIdsBySeller(sellerId);
        if (productIds.isEmpty()) {
            return List.of();
        }

        return enrollmentRepository.findByCourseIdIn(productIds).stream()
                .map(EnrollmentDto.SellerOrderResponse::from)
                .collect(Collectors.toList());
    }

    private String normalizeCategory(String category) {
        if (category == null) return null;

        return switch (category) {
            case "FASHION" -> "패션";
            case "BEAUTY" -> "뷰티";
            case "FOOD" -> "식품";
            case "DIGITAL" -> "디지털";
            case "HOME" -> "홈/리빙";
            case "SPORTS" -> "스포츠";
            case "BOOK" -> "도서";
            default -> category;
        };
    }

    private Long toLong(Object value) {
        if (value == null) return null;
        if (value instanceof Number number) return number.longValue();
        return Long.parseLong(value.toString());
    }

    private Integer toInteger(Object value) {
        if (value == null) return null;
        if (value instanceof Number number) return number.intValue();
        return Integer.parseInt(value.toString());
    }

    private String firstNonNull(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }
        return null;
    }

    private Object firstNonNullObject(Object... values) {
        for (Object value : values) {
            if (value != null) {
                return value;
            }
        }
        return null;
    }
}