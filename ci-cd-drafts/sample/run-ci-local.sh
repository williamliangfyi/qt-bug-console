#!/usr/bin/env bash
# Local mirror of .github/workflows/ci.yml (format + build-test jobs).
# Usage:
#   ./run-ci-local.sh         run both "jobs" like CI does
#   ./run-ci-local.sh --fix   auto-format sources (clang-format -i), then run
set -uo pipefail

cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"

SOURCES=$(find src tests -name '*.cpp' -o -name '*.hpp')

if [[ "${1:-}" == "--fix" ]]; then
  echo ">> auto-formatting sources"
  clang-format -i $SOURCES
fi

echo "==> job: format (clang-format)"
if clang-format --dry-run --Werror $SOURCES; then
  echo "   format: PASS"
  fmt=0
else
  echo "   format: FAIL  (run ./run-ci-local.sh --fix)"
  fmt=1
fi

echo "==> job: build-test (cmake + ctest)"
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake --build build --parallel >/dev/null
if ctest --test-dir build --output-on-failure; then
  echo "   build-test: PASS"
  bt=0
else
  echo "   build-test: FAIL"
  bt=1
fi

echo "==> summary: format=$([[ $fmt -eq 0 ]] && echo PASS || echo FAIL)  build-test=$([[ $bt -eq 0 ]] && echo PASS || echo FAIL)"
exit $(( fmt || bt ))
