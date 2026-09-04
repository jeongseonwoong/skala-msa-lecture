#!/usr/bin/env bash
#
# 네트워크 없이(Maven/Gradle 미사용) 로컬 소스를 기존 도커 이미지에 얹기 위한 빌드.
#
#   - Java 서비스(user/course/enrollment): 기존 이미지 안의 BOOT-INF/lib/*.jar 를
#     컴파일 클래스패스로 삼아 javac 로 src/main/java 전체를 재컴파일하고,
#     app.jar 의 BOOT-INF/classes 만 교체한 패치 jar 를 만든다.
#   - auth-server: 소스가 배포되지 않는 사전 빌드 이미지. src/main/java 에는 enum 패치를
#     위한 User.java 만 있으므로, BOOT-INF/classes 를 통째로 갈지 않고 재컴파일된
#     User*.class 3개만 원본 app.jar 위에 덮어쓴다 (surgical patch).
#   - recommend-service(Python): 컴파일 불필요. docker-compose.override.yml 이
#     소스 디렉터리를 컨테이너에 그대로 마운트한다.
#
# 산출물: <service>/build-local/app.jar  (docker-compose.override.yml 이 마운트)
#
# 사용:
#   ./scripts/build-local.sh                  # auth + user + course + enrollment 전부
#   ./scripts/build-local.sh user-service     # 하나만
#   ./scripts/build-local.sh auth-server
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JAVA_SERVICES=(user-service course-service enrollment-service)   # BOOT-INF/classes 전체 교체
ALL_SERVICES=(auth-server "${JAVA_SERVICES[@]}")
SERVICES=("${@:-${ALL_SERVICES[@]}}")

command -v javac >/dev/null || { echo "javac(JDK 21) 필요"; exit 1; }
command -v docker >/dev/null || { echo "docker 필요"; exit 1; }

LOMBOK="$(find "$HOME/.m2" "$HOME/.gradle" -name 'lombok-*.jar' ! -name '*-sources.jar' 2>/dev/null | sort -V | tail -1 || true)"
[ -n "$LOMBOK" ] || { echo "lombok jar 를 찾지 못했습니다 (~/.m2, ~/.gradle)"; exit 1; }
echo "lombok: $LOMBOK"

# auth-server: app.jar 안의 User*.class 3개만 교체 (나머지 원본 유지)
patch_auth_server() {
  local img="msa-lecture/auth-server:1.0"
  local work="$ROOT/auth-server/build-local"
  echo "=== auth-server  ($img)  [surgical]"
  docker image inspect "$img" >/dev/null 2>&1 || { echo "  이미지 없음: $img (이미지 아카이브 먼저 load)"; exit 1; }

  rm -rf "$work"; mkdir -p "$work/ex" "$work/classes" "$work/stage/BOOT-INF/classes"
  local cid; cid="$(docker create "$img")"
  docker cp "$cid:/app/app.jar" "$work/app.jar"
  docker rm "$cid" >/dev/null

  ( cd "$work/ex" && unzip -oq "$work/app.jar" 'BOOT-INF/lib/*' )
  local cp; cp="$(printf '%s:' "$work"/ex/BOOT-INF/lib/*.jar)$LOMBOK"

  find "$ROOT/auth-server/src/main/java" -name '*.java' > "$work/sources.txt"
  echo "  컴파일: $(wc -l < "$work/sources.txt" | tr -d ' ') files"
  javac -encoding UTF-8 --release 21 -parameters -proc:full -cp "$cp" -d "$work/classes" "@$work/sources.txt"

  cp -R "$work/classes"/. "$work/stage/BOOT-INF/classes/"
  ( cd "$work/stage" && zip -q -r "$work/app.jar" BOOT-INF/classes )   # 기존 엔트리만 갱신

  rm -rf "$work/ex" "$work/classes" "$work/stage" "$work/sources.txt"
  echo "  -> $work/app.jar  ($(du -h "$work/app.jar" | cut -f1))  — User*.class 교체됨"
}

# user/course/enrollment: BOOT-INF/classes 전체를 재컴파일 결과로 교체
patch_full_java() {
  local s="$1"
  local img="msa-lecture-${s}:latest"
  local work="$ROOT/$s/build-local"
  echo "=== $s  ($img)"
  docker image inspect "$img" >/dev/null 2>&1 || { echo "  이미지 없음: $img"; exit 1; }

  rm -rf "$work"; mkdir -p "$work/ex"
  local cid; cid="$(docker create "$img")"
  docker cp "$cid:/app/app.jar" "$work/app.orig.jar"
  docker rm "$cid" >/dev/null

  ( cd "$work/ex" && unzip -oq ../app.orig.jar )

  local cp; cp="$(printf '%s:' "$work"/ex/BOOT-INF/lib/*.jar)$LOMBOK"
  local classout="$work/classes"; rm -rf "$classout"; mkdir -p "$classout"
  find "$ROOT/$s/src/main/java" -name '*.java' > "$work/sources.txt"
  echo "  컴파일: $(wc -l < "$work/sources.txt" | tr -d ' ') files"
  # -parameters: Spring MVC 가 @PathVariable/@RequestParam 이름을 리플렉션으로 얻으려면 필수
  javac -encoding UTF-8 --release 21 -parameters -proc:full -cp "$cp" -d "$classout" "@$work/sources.txt"

  # BOOT-INF/classes = 새로 컴파일한 클래스 + 리소스
  rm -rf "$work/ex/BOOT-INF/classes"; mkdir -p "$work/ex/BOOT-INF/classes"
  cp -R "$classout"/. "$work/ex/BOOT-INF/classes/"
  [ -d "$ROOT/$s/src/main/resources" ] && cp -R "$ROOT/$s/src/main/resources"/. "$work/ex/BOOT-INF/classes/"

  # 재패키징: BOOT-INF/lib/*.jar 는 반드시 STORED(무압축) — Spring Boot 로더 요구사항
  rm -f "$work/app.jar"
  ( cd "$work/ex"
    zip -q -r -0 "$work/app.jar" BOOT-INF/lib
    zip -q -r    "$work/app.jar" . -x 'BOOT-INF/lib/*' )

  rm -rf "$work/ex" "$work/classes" "$work/app.orig.jar" "$work/sources.txt"
  echo "  -> $work/app.jar  ($(du -h "$work/app.jar" | cut -f1))"
}

for s in "${SERVICES[@]}"; do
  if [ "$s" = "auth-server" ]; then
    patch_auth_server
    continue
  fi
  case " ${JAVA_SERVICES[*]} " in
    *" $s "*) patch_full_java "$s" ;;
    *) echo "건너뜀(지원 서비스 아님): $s" ;;
  esac
done

echo
echo "완료. 다음으로:"
echo "  docker compose up -d --force-recreate       # override 가 패치 jar / recommend 소스를 마운트"
echo "  # 재기동 후 ~15s 대기 (Eureka 재등록 전엔 서비스 간 호출이 503)"
case " ${SERVICES[*]} " in
  *" auth-server "*)
    echo "  docker compose restart api-gateway recommend-service   # auth 재기동 → JWKS 바뀜, 검증 측 캐시 갱신"
    ;;
esac
