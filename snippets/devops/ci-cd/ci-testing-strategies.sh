#!/bin/bash
# Comprehensive testing strategies for CI/CD

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Unit tests
run_unit_tests() {
    log_info "Running unit tests..."
    npm run test:unit -- --coverage --ci --maxWorkers=2

    # Check coverage thresholds
    if [ -f "coverage/coverage-summary.json" ]; then
        coverage=$(node -p "JSON.parse(require('fs').readFileSync('coverage/coverage-summary.json')).total.lines.pct")
        if (( $(echo "$coverage < 80" | bc -l) )); then
            log_error "Coverage below 80%: ${coverage}%"
            exit 1
        fi
        log_info "Coverage: ${coverage}%"
    fi
}

# Integration tests
run_integration_tests() {
    log_info "Running integration tests..."

    # Start dependencies
    docker-compose -f docker-compose.test.yml up -d

    # Wait for services
    log_info "Waiting for services..."
    sleep 10

    # Run tests
    npm run test:integration

    # Cleanup
    docker-compose -f docker-compose.test.yml down -v
}

# E2E tests
run_e2e_tests() {
    log_info "Running E2E tests..."

    # Build application
    npm run build

    # Start application
    npm run start &
    APP_PID=$!

    # Wait for app to be ready
    timeout 60 bash -c 'until curl -f http://localhost:3000/health; do sleep 2; done'

    # Run Playwright tests
    npx playwright test

    # Cleanup
    kill $APP_PID
}

# Load/Performance tests
run_performance_tests() {
    log_info "Running performance tests..."

    # Using k6
    if command -v k6 &> /dev/null; then
        k6 run tests/load/basic-load-test.js
    else
        log_warn "k6 not installed, skipping performance tests"
    fi
}

# Security tests
run_security_tests() {
    log_info "Running security tests..."

    # Dependency scanning
    npm audit --audit-level=high

    # SAST scanning
    if command -v semgrep &> /dev/null; then
        semgrep --config=auto .
    fi

    # Secret scanning
    if command -v trufflehog &> /dev/null; then
        trufflehog filesystem . --json
    fi
}

# Smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."

    # Check health endpoint
    if ! curl -f http://localhost:3000/health; then
        log_error "Health check failed"
        return 1
    fi

    # Check critical endpoints
    curl -f http://localhost:3000/api/status

    log_info "Smoke tests passed"
}

# Contract tests (Pact)
run_contract_tests() {
    log_info "Running contract tests..."

    if [ -f "pact/consumer-tests.js" ]; then
        npm run test:contract
    else
        log_warn "No contract tests found"
    fi
}

# Visual regression tests
run_visual_tests() {
    log_info "Running visual regression tests..."

    if command -v percy &> /dev/null; then
        percy exec -- npm run test:visual
    else
        log_warn "Percy not installed, skipping visual tests"
    fi
}

# Accessibility tests
run_accessibility_tests() {
    log_info "Running accessibility tests..."

    if command -v pa11y &> /dev/null; then
        pa11y-ci
    else
        log_warn "pa11y not installed, skipping accessibility tests"
    fi
}

# Main test execution
main() {
    local test_type="${1:-all}"

    case $test_type in
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        e2e)
            run_e2e_tests
            ;;
        performance)
            run_performance_tests
            ;;
        security)
            run_security_tests
            ;;
        smoke)
            run_smoke_tests
            ;;
        contract)
            run_contract_tests
            ;;
        visual)
            run_visual_tests
            ;;
        accessibility)
            run_accessibility_tests
            ;;
        all)
            run_unit_tests
            run_integration_tests
            run_security_tests
            ;;
        *)
            log_error "Unknown test type: $test_type"
            echo "Usage: $0 {unit|integration|e2e|performance|security|smoke|contract|visual|accessibility|all}"
            exit 1
            ;;
    esac

    log_info "Tests completed successfully!"
}

main "$@"
