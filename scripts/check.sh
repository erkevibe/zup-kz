#!/bin/sh
set -eu

python3 tests/assert_lifecycle_token_scope.py
python3 tests/assert_organization_guard_coverage.py
sh -n scripts/*.sh

if find src/main/lsfusion -type f -name '*Test.lsf' -print -quit | grep -q .; then
    echo 'Test modules must live under src/test/lsfusion' >&2
    exit 1
fi

echo STATIC_CHECKS_OK
