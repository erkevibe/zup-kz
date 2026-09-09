#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
platform_dir=${1:-"$project_dir/../platform"}
expected_revision=$(tr -d '\r\n' < "$project_dir/platform-revision.txt")
actual_revision=$(git -C "$platform_dir" rev-parse HEAD)

if [ "$actual_revision" != "$expected_revision" ]; then
    echo "Platform revision mismatch: expected $expected_revision, got $actual_revision" >&2
    exit 1
fi

mvn --batch-mode --file "$platform_dir/pom.xml" \
    -pl :server,:web-compile-maven-plugin -am install -DskipTests

profiles=${ZUP_BUILD_PROFILES:-assemble,embed-server}
case ",$profiles," in
    *,test-logics,*)
        mvn --batch-mode --no-snapshot-updates --file "$project_dir/pom.xml" \
            clean package -Passemble,embed-server
        if jar tf "$project_dir/target/lsfusion-server-0.1.0-SNAPSHOT.jar" |
            grep -q 'Test\.lsf$'; then
            echo 'Production JAR contains test modules' >&2
            exit 1
        fi
        mvn --batch-mode --no-snapshot-updates --file "$project_dir/pom.xml" \
            package -P"$profiles"
        ;;
    *)
        mvn --batch-mode --no-snapshot-updates --file "$project_dir/pom.xml" \
            clean package -P"$profiles"
        ;;
esac
