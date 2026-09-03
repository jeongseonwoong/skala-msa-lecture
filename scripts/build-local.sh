#!/usr/bin/env bash
#
# 네트워크 없이(Maven/Gradle 미사용) 로컬 소스를 기존 도커 이미지에 얹기 위한 빌드.
#
#   - Java 서비스(user/course/enrollment): 기존 이미지 안의 BOOT-INF/lib/*.jar 를
#     컴파일 클래스패스로 삼아 javac 로 src/main/java 전체를 재컴파일하고,
#     app.jar 의 BOOT-INF/classes 만 교체한 패치 jar 를 만든다.
#   - recommend-service(Python): 컴파일 불필요. docker-compose.override.yml 이
#     소스 디렉터리를 컨테이너에 그대로 마운트한다.
#
# 산출물: <service>/build-local/app.jar  (docker-compose.override.yml 이 마운트)
#
# 사용:
#   ./scripts/build-local.sh            # 3개 서비스 모두
#   ./scripts/build-local.sh user-service
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JAVA_SERVICES=(user-service course-service enrollment-service)
SERVICES=("${@:-${JAVA_SERVICES[@]}}")

command -v javac >/dev/null || { echo "javac(JDK 21) 필요"; exit 1; }
command -v docker >/dev/null || { echo "docker 필요"; exit 1; }

LOMBOK="$(find "$HOME/.m2" "$HOME/.gradle" -name 'lombok-*.jar' ! -name '*-sources.jar' 2>/dev/null | sort -V | tail -1 || true)"
[ -n "$LOMBOK" ] || { echo "lombok jar 를 찾지 못했습니다 (~/.m2, ~/.gradle)"; exit 1; }
echo "lombok: $LOMBOK"

for s in "${SERVICES[@]}"; do
  case " ${JAVA_SERVICES[*]} " in *" $s "*) ;; *) echo "건너뜀(자바 서비스 아님): $s"; continue ;; esac

  img="msa-lecture-${s}:latest"
  work="$ROOT/$s/build-local"
  echo "=== $s  ($img) ==="
  docker image inspect "$img" >/dev/null 2>&1 || { echo "  이미지 없음: $img"; exit 1; }

  rm -rf "$work"; mkdir -p "$work/ex"
  cid="$(docker create "$img")"
  docker cp "$cid:/app/app.jar" "$work/app.orig.jar"
  docker rm "$cid" >/dev/null

  ( cd "$work/ex" && unzip -oq ../app.orig.jar )

  cp="$(printf '%s:' "$work"/ex/BOOT-INF/lib/*.jar)$LOMBOK"
  classout="$work/classes"; rm -rf "$classout"; mkdir -p "$classout"
  find "$ROOT/$s/src/main/java" -name '*.java' > "$work/sources.txt"
  echo "  컴파일: $(wc -l < "$work/sources.txt") files"
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
done

echo
echo "완료. 다음으로:"
echo "  docker compose up -d          # override 가 패치 jar / recommend 소스를 마운트"
echo "  docker compose restart user-service course-service enrollment-service recommend-service"
