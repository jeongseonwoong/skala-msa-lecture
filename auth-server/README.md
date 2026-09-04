# auth-server (부분 소스)

auth-server 는 강의에서 **사전 빌드된 도커 이미지**(`msa-lecture/auth-server:1.0`)로만
배포된다. 전체 소스가 없고 재빌드도 불가능하다 (이미지 아카이브로 배포).

## 왜 이 디렉터리에 소스 한 개만 있나

신 도메인 시드 데이터는 사용자 `role` 을 `MD` / `SELLER` / `BUYER` 로 넣는다.
그런데 이미지 안의 `com.lecture.auth.model.User.Role` enum 은 구 도메인 값인
`STUDENT` / `INSTRUCTOR` 만 알고 있다. 그래서 어떤 계정으로 로그인하든
`CustomUserDetailsService.loadUserByUsername` → Hibernate 가 다음으로 실패한다:

```
No enum constant com.lecture.auth.model.User.Role.MD
```

`src/main/java/com/lecture/auth/model/User.java` 는 이미지의 `User` 클래스 형태를
(javap 로 확인해) 그대로 복원하고 enum 에 `MD/SELLER/BUYER` 를 추가한 **최소 파일**이다.
auth-server 전체 소스가 아니다.

## 패치 jar 만들기

```bash
./scripts/build-local.sh auth-server
```

동작:
1. `msa-lecture/auth-server:1.0` 에서 `app.jar` 추출
2. 그 jar 의 `BOOT-INF/lib/*.jar` 를 클래스패스로 `User.java` 만 재컴파일
3. `app.jar` 안 `BOOT-INF/classes/.../User.class`, `User$Role.class`,
   `User$UserBuilder.class` **3개만** 덮어씀 (나머지 클래스·설정은 원본 유지)
4. 결과 → `auth-server/build-local/app.jar` (git 무시됨)

`docker-compose.override.yml` 이 이 jar 를 컨테이너의 `/app/app.jar` 로 마운트한다.

## 적용

```bash
./scripts/build-local.sh                       # auth + user + course + enrollment
docker compose up -d --force-recreate auth-server
```

### ⚠️ auth-server 를 재기동하면 api-gateway · recommend-service 도 재기동

auth-server 는 서명 키(RSA)를 메모리에서 매번 새로 만든다. 재기동하면 JWKS 가 바뀌는데
JWT 를 검증하는 쪽이 옛 공개키를 캐시하고 있으면 토큰 검증이 깨진다:

- **recommend-service** (FastAPI): 기동 시 JWKS 를 한 번만 받음 → `401 "일치하는 공개키를 찾을 수 없습니다"`
- **api-gateway**: JWKS 캐시 갱신이 안 되면 `X-User-Id` 주입 실패 → `/api/users/me` 등이 `500`
  (게이트웨이가 주입하는 헤더에 의존하는 엔드포인트)

user/course/enrollment(Spring resource server)는 대개 자동 갱신되지만, 확실히 하려면 셋 다:

```bash
docker compose restart api-gateway recommend-service
```
