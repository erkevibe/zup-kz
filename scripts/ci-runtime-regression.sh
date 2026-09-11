#!/bin/sh
set -eu
umask 077

server_log=${ZUP_SERVER_LOG:-server.log}
server_jar=${ZUP_SERVER_JAR:-target/lsfusion-server-0.1.0-SNAPSHOT.jar}
http_port=${ZUP_TEST_HTTP_PORT:-7651}
rmi_port=${ZUP_TEST_RMI_PORT:-7652}
websocket_port=${ZUP_TEST_WEBSOCKET_PORT:-8887}
endpoint=${ZUP_TEST_ENDPOINT:-http://localhost:$http_port/exec}
admin_credentials=${ZUP_TEST_ADMIN_CREDENTIALS:-admin:ci-admin-only}
request_timeout=${ZUP_TEST_REQUEST_TIMEOUT:-600}
run_id=${ZUP_TEST_RUN_ID:-${GITHUB_RUN_ID:-local-runtime}}
action_manifest=${ZUP_ACTION_MANIFEST:-runtime-action-manifest.tsv}
server_pid=
run_started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)

if [ ! -f "$server_jar" ]; then
    echo "Runtime JAR not found: $server_jar" >&2
    exit 1
fi
newer_logic=$(find src/main/lsfusion src/test/lsfusion -type f -name '*.lsf' -newer "$server_jar" -print -quit)
if [ -n "$newer_logic" ]; then
    echo "Runtime JAR is stale; rebuild after changing: $newer_logic" >&2
    exit 1
fi

printf 'run_id\tstarted_at\tfinished_at\tuser\taction\texpectation\tresult\toutput\tsha256\n' > "$action_manifest"

cleanup() {
    exit_status=$?
    if [ -n "$server_pid" ]; then
        kill -TERM "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
    finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    printf '%s\t%s\t%s\t-\tfinal-run\tverification\tFAIL\t-\t-\n' \
        "$run_id" "$run_started_at" "$finished_at" >> "$action_manifest"
    return "$exit_status"
}
trap cleanup EXIT HUP INT TERM

request_as() {
    credentials=$1
    action=$2
    output=$3
    request_user=${credentials%%:*}
    started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    case "$action" in
        *Attack*|*Guard*|*Tamper*|*SnapshotDelete*|*SnapshotInsert*)
            expectation=expected-negative
            ;;
        *Setup*|*Verification*)
            expectation=verification
            ;;
        *)
            expectation=positive
            ;;
    esac
    if curl --fail --silent --show-error --connect-timeout 10 \
        --max-time "$request_timeout" --user "$credentials" \
        "$endpoint?action=ZUPKZ.$action" --output "$output"; then
        finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
        output_hash=$(sha256sum "$output" | cut -d' ' -f1)
        printf '%s\t%s\t%s\t%s\t%s\t%s\tPASS\t%s\t%s\n' \
            "$run_id" "$started_at" "$finished_at" "$request_user" "$action" \
            "$expectation" "$output" "$output_hash" >> "$action_manifest"
    else
        request_rc=$?
        finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
        printf '%s\t%s\t%s\t%s\t%s\t%s\tFAIL\t%s\t-\n' \
            "$run_id" "$started_at" "$finished_at" "$request_user" "$action" \
            "$expectation" "$output" >> "$action_manifest"
        return "$request_rc"
    fi
}

request() {
    request_as "$admin_credentials" "$1" "$2"
}

check() {
    action=$1
    output=$2
    assertion=$3
    request "$action" "$output"
    assertion_started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    assertion_name=$(basename "$assertion" .py)
    if python3 "$assertion" "$output"; then
        assertion_finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
        printf '%s\t%s\t%s\t-\t%s\tassertion\tPASS\t%s\t%s\n' \
            "$run_id" "$assertion_started_at" "$assertion_finished_at" \
            "$assertion_name" "$output" "$(sha256sum "$output" | cut -d' ' -f1)" \
            >> "$action_manifest"
    else
        assertion_finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
        printf '%s\t%s\t%s\t-\t%s\tassertion\tFAIL\t%s\t-\n' \
            "$run_id" "$assertion_started_at" "$assertion_finished_at" \
            "$assertion_name" "$output" >> "$action_manifest"
        return 1
    fi
}

java -Xms256m -Xmx2g -Dhttp.port="$http_port" -Drmi.port="$rmi_port" \
    -DwebSocket.port="$websocket_port" \
    -jar "$server_jar" > "$server_log" 2>&1 &
server_pid=$!

attempt=0
until grep -q 'Server has successfully started' "$server_log"; do
    if ! kill -0 "$server_pid" 2>/dev/null; then
        cat "$server_log"
        exit 1
    fi
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 180 ]; then
        cat "$server_log"
        exit 1
    fi
    sleep 1
done

check uiRoleSetupTest ui-role-setup-result.json tests/assert_ui_role_setup.py
check initialRolePermissionsTest initial-role-permissions-result.json tests/assert_ui_role_setup.py
check payrollFormulaTest payroll-result.json tests/assert_payroll.py
request bankRegisterLineSnapshotTamperTest bank-register-line-tamper-result.json
request bankRegisterHeaderSnapshotTamperTest bank-register-header-tamper-result.json
request bankRegisterLineSnapshotDeleteTest bank-register-line-delete-result.json
request bankRegisterLineSnapshotInsertTest bank-register-line-insert-result.json
request bankRegisterSnapshotVerificationTest bank-register-snapshot-verification-result.json
python3 tests/assert_bank_register_snapshot.py \
    bank-register-line-tamper-result.json bank-register-header-tamper-result.json \
    bank-register-line-delete-result.json bank-register-line-insert-result.json \
    bank-register-snapshot-verification-result.json
check payrollLegalScenarioTest payroll-legal-scenarios-result.json tests/assert_payroll_legal_scenarios.py
check civilContractLegalScenarioTest civil-contract-legal-scenarios-result.json tests/assert_civil_contract_legal_scenarios.py
check incomeTaxBoundaryScenarioTest income-tax-boundaries-result.json tests/assert_income_tax_boundaries.py
check payrollClosureWorkflowTest payroll-closure-workflow-result.json tests/assert_payroll_closure_workflow.py

request payrollConcurrencySetupTest payroll-concurrency-setup-result.json
request payrollConcurrentCloseTest payroll-concurrency-close-1.json &
close_pid_1=$!
request payrollConcurrentCloseTest payroll-concurrency-close-2.json &
close_pid_2=$!
wait "$close_pid_1" || true
wait "$close_pid_2" || true
check payrollConcurrencyVerificationTest payroll-concurrency-result.json tests/assert_payroll_concurrency.py

check payrollResetWorkflowTest payroll-reset-workflow-result.json tests/assert_payroll_reset_workflow.py

request payrollRecalculationWorkflowTest payroll-recalculation-workflow-result.json
request recalculationLineSnapshotGuardTest recalculation-line-guard-result.json
request recalculationInputSnapshotGuardTest recalculation-input-guard-result.json
request recalculationPeriodGuardTest recalculation-period-guard-result.json
request recalculationWorkflowVerificationTest recalculation-verification-result.json
python3 tests/assert_payroll_recalculation_workflow.py \
    payroll-recalculation-workflow-result.json \
    recalculation-line-guard-result.json \
    recalculation-input-guard-result.json \
    recalculation-verification-result.json \
    recalculation-period-guard-result.json

check statutoryGuardTest statutory-guard-result.json tests/assert_statutory_guards.py
check payrollStage0Test stage0-result.json tests/assert_stage0.py

request hrWorkflowTest hr-workflow-result.json
request employmentLegacyFieldsGuardTest employment-legacy-guard-result.json
request employmentSourceOfTruthVerificationTest employment-source-verification-result.json
python3 tests/assert_hr_workflow.py \
    hr-workflow-result.json employment-legacy-guard-result.json \
    employment-source-verification-result.json

request timeWorkflowTest time-workflow-result.json
request scheduleOverlapGuardTest schedule-overlap-guard-result.json
request scheduleOverlapGuardVerificationTest schedule-overlap-verification-result.json
time_guard_actions='scheduleCycleOwnershipGuardTest scheduleCycleDayOffGuardTest scheduleCycleDuplicateDayGuardTest scheduleOrganizationGuardTest scheduleEmploymentPeriodGuardTest scheduleValidityPeriodGuardTest scheduleCycleGapGuardTest scheduleCycleStartRequiredGuardTest scheduleCycleStartAfterAssignmentGuardTest shiftPlannedHoursGuardTest overnightShiftDurationTest'
for action in $time_guard_actions; do
    request "$action" "$action-result.json"
done
python3 tests/assert_time_workflow.py \
    time-workflow-result.json schedule-overlap-guard-result.json \
    schedule-overlap-verification-result.json \
    scheduleCycleOwnershipGuardTest-result.json \
    scheduleCycleDayOffGuardTest-result.json \
    scheduleCycleDuplicateDayGuardTest-result.json \
    scheduleOrganizationGuardTest-result.json \
    scheduleEmploymentPeriodGuardTest-result.json \
    scheduleValidityPeriodGuardTest-result.json \
    scheduleCycleGapGuardTest-result.json \
    scheduleCycleStartRequiredGuardTest-result.json \
    scheduleCycleStartAfterAssignmentGuardTest-result.json \
    shiftPlannedHoursGuardTest-result.json overnightShiftDurationTest-result.json

check leaveWorkflowTest leave-workflow-result.json tests/assert_leave_workflow.py
check sickLeaveWorkflowTest sick-leave-workflow-result.json tests/assert_sick_leave_workflow.py

request accessWorkflowTest access-workflow-result.json
request_as zup-access-test:zup-access-ci-only crossOrganizationPolicyTest cross-organization-policy-result.json
request_as zup-access-test:zup-access-ci-only crossOrganizationStatusAttackTest cross-organization-attack-result.json
request_as zup-access-hr:zup-ui-test-only crossOrganizationMasterDataAttackTest cross-organization-master-data-attack-result.json
request_as zup-access-time:zup-ui-test-only crossOrganizationDraftAttackTest cross-organization-draft-attack-result.json
request_as zup-access-payroll:zup-ui-test-only crossOrganizationPayrollAttackTest cross-organization-payroll-attack-result.json
request_as zup-access-chief:zup-ui-test-only crossOrganizationOwnershipAttackTest cross-organization-ownership-attack-result.json
request_as zup-access-hr:zup-ui-test-only crossOrganizationDeleteAttackTest cross-organization-delete-attack-result.json
request_as zup-access-hr:zup-ui-test-only crossOrganizationSecondaryHrAttackTest cross-organization-secondary-hr-attack-result.json
request_as zup-access-payroll:zup-ui-test-only crossOrganizationSecondaryPayrollAttackTest cross-organization-secondary-payroll-attack-result.json
request_as zup-access-chief:zup-ui-test-only crossOrganizationSecondaryReportAttackTest cross-organization-secondary-report-attack-result.json
request_as zup-access-chief:zup-ui-test-only crossOrganizationSecondaryOwnershipAttackTest cross-organization-secondary-ownership-attack-result.json
request_as zup-access-hr:zup-ui-test-only crossOrganizationSecondaryDeleteAttackTest cross-organization-secondary-delete-attack-result.json
request crossOrganizationVerificationTest cross-organization-verification-result.json
request paymentAccountSecuritySetupTest payment-account-security-setup-result.json
request_as zup-access-time:zup-ui-test-only sameOrganizationTimekeeperEmployeeAttackTest \
    same-organization-timekeeper-employee-attack-result.json
request_as zup-access-time:zup-ui-test-only sameOrganizationTimekeeperOrganizationAttackTest \
    same-organization-timekeeper-organization-attack-result.json
request_as zup-access-payroll:zup-ui-test-only sameOrganizationPayrollPaymentAccountAttackTest \
    same-organization-payroll-account-attack-result.json
request_as zup-access-payroll:zup-ui-test-only sameOrganizationPayrollDepartmentAttackTest \
    same-organization-payroll-department-attack-result.json
request_as zup-access-time:zup-ui-test-only sameOrganizationTimekeeperPayrollAttackTest \
    same-organization-timekeeper-payroll-attack-result.json
request_as zup-access-payroll:zup-ui-test-only sameOrganizationPayrollWorkingTimeAttackTest \
    same-organization-payroll-working-time-attack-result.json
request_as zup-access-payroll:zup-ui-test-only sameOrganizationPayrollPersonnelAttackTest \
    same-organization-payroll-personnel-attack-result.json
request_as zup-access-payroll:zup-ui-test-only sameOrganizationPayrollTaxesAttackTest \
    same-organization-payroll-taxes-attack-result.json
request_as zup-access-hr:zup-ui-test-only crossOrganizationPaymentAccountReadTest \
    cross-organization-payment-account-read-result.json
request_as zup-access-hr:zup-ui-test-only crossOrganizationPaymentAccountMutationAttackTest \
    cross-organization-payment-account-mutation-result.json
request_as zup-access-hr:zup-ui-test-only crossOrganizationPaymentAccountReparentAttackTest \
    cross-organization-payment-account-reparent-result.json
request_as zup-access-hr:zup-ui-test-only crossOrganizationPaymentAccountDeleteAttackTest \
    cross-organization-payment-account-delete-result.json
request_as zup-access-hr:zup-ui-test-only crossOrganizationHiddenEmployeePaymentAccountAttackTest \
    cross-organization-hidden-employee-account-result.json
request_as zup-access-hr:zup-ui-test-only crossOrganizationHiddenEmployeeEmploymentAttackTest \
    cross-organization-hidden-employee-employment-result.json
request paymentAccountOverlapGuardTest payment-account-overlap-guard-result.json
request paymentAccountOverlapEditGuardTest payment-account-overlap-edit-guard-result.json
request verticalRoleAttackVerificationTest vertical-role-attack-verification-result.json
python3 tests/assert_vertical_role_attacks.py \
    cross-organization-payment-account-read-result.json \
    payment-account-overlap-guard-result.json \
    payment-account-overlap-edit-guard-result.json \
    vertical-role-attack-verification-result.json
request_as zup-access-time:zup-ui-test-only sameOrganizationTimekeeperAllowedTest \
    same-organization-timekeeper-allowed-result.json
request_as zup-access-payroll:zup-ui-test-only sameOrganizationPayrollAllowedTest \
    same-organization-payroll-allowed-result.json
request_as zup-access-hr:zup-ui-test-only sameOrganizationHrAllowedTest \
    same-organization-hr-allowed-result.json
request_as zup-access-chief:zup-ui-test-only sameOrganizationChiefTaxAllowedTest \
    same-organization-chief-tax-allowed-result.json
request legacyPaymentAccountMigrationTest legacy-payment-account-migration-result.json
request paymentAccountSecurityVerificationTest payment-account-security-verification-result.json
for action in employeeIinFormatGuardTest organizationBinFormatGuardTest bankDetailsFormatGuardTest; do
    request "$action" "$action-result.json"
done
python3 tests/assert_access_workflow.py \
    access-workflow-result.json cross-organization-policy-result.json \
    cross-organization-verification-result.json \
    payment-account-security-setup-result.json payment-account-overlap-guard-result.json \
    payment-account-security-verification-result.json legacy-payment-account-migration-result.json \
    employeeIinFormatGuardTest-result.json organizationBinFormatGuardTest-result.json \
    bankDetailsFormatGuardTest-result.json

request employeeCabinetSetupTest employee-cabinet-setup-result.json
request employeeCabinetAccessTest employee-cabinet-access-result.json
request employeeCabinetFixtureVerificationTest employee-cabinet-verification-result.json
python3 tests/assert_employee_cabinet.py \
    employee-cabinet-setup-result.json employee-cabinet-access-result.json \
    employee-cabinet-verification-result.json
check printWorkflowTest print-workflow-result.json tests/assert_print_workflow.py
check employeeCardWorkflowTest employee-card-workflow-result.json tests/assert_employee_card_workflow.py
check planningWorkflowTest planning-workflow-result.json tests/assert_planning_workflow.py

request approvalWorkflowTest approval-workflow-result.json
request approvalBlockVerificationTest approval-block-result.json
python3 tests/assert_approval_workflow.py approval-workflow-result.json approval-block-result.json

check archiveWorkflowTest archive-workflow-result.json tests/assert_archive_workflow.py
check insuranceWorkflowTest insurance-workflow-result.json tests/assert_insurance_workflow.py

lifecycle_actions='lifecycleGuardSetupTest timesheetStatusGuardTest payrollStatusGuardTest socialStatusGuardTest payrollSnapshotGuardTest payrollSnapshotDeleteGuardTest taxSnapshotGuardTest personnelEventStatusGuardTest esutdStatusGuardTest esutdResponseGuardTest paymentStatementStatusGuardTest paymentStatementSnapshotGuardTest form200StatusGuardTest form200SnapshotGuardTest approvalStatusGuardTest approvalStepStatusGuardTest archiveStatusGuardTest archiveDocumentStatusGuardTest insurancePolicyStatusGuardTest insurancePolicySnapshotGuardTest workAccidentStatusGuardTest insuranceClaimStatusGuardTest leaveStatusGuardTest vacationScheduleStatusGuardTest tripStatusGuardTest averageStatusGuardTest civilContractStatusGuardTest civilActStatusGuardTest civilLiabilityStatusGuardTest enforcementOrderStatusGuardTest enforcementCalculationStatusGuardTest interimPaymentStatusGuardTest bankRegisterStatusGuardTest liabilityStatusGuardTest recalculationStatusGuardTest sickLeaveStatusGuardTest socialTransferStatusGuardTest lifecycleGuardVerificationTest'
for action in $lifecycle_actions; do
    request "$action" "$action.json"
done
python3 tests/assert_lifecycle_guards.py \
    lifecycleGuardSetupTest.json timesheetStatusGuardTest.json \
    payrollStatusGuardTest.json socialStatusGuardTest.json \
    payrollSnapshotGuardTest.json payrollSnapshotDeleteGuardTest.json \
    taxSnapshotGuardTest.json personnelEventStatusGuardTest.json \
    esutdStatusGuardTest.json esutdResponseGuardTest.json \
    paymentStatementStatusGuardTest.json paymentStatementSnapshotGuardTest.json \
    form200StatusGuardTest.json form200SnapshotGuardTest.json \
    approvalStatusGuardTest.json approvalStepStatusGuardTest.json \
    archiveStatusGuardTest.json archiveDocumentStatusGuardTest.json \
    insurancePolicyStatusGuardTest.json insurancePolicySnapshotGuardTest.json \
    workAccidentStatusGuardTest.json insuranceClaimStatusGuardTest.json \
    leaveStatusGuardTest.json vacationScheduleStatusGuardTest.json \
    tripStatusGuardTest.json averageStatusGuardTest.json \
    civilContractStatusGuardTest.json civilActStatusGuardTest.json \
    civilLiabilityStatusGuardTest.json enforcementOrderStatusGuardTest.json \
    enforcementCalculationStatusGuardTest.json interimPaymentStatusGuardTest.json \
    bankRegisterStatusGuardTest.json liabilityStatusGuardTest.json \
    recalculationStatusGuardTest.json sickLeaveStatusGuardTest.json \
    socialTransferStatusGuardTest.json lifecycleGuardVerificationTest.json

kill -TERM "$server_pid"
wait "$server_pid" || true
server_pid=
finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf '%s\t%s\t%s\t-\tfinal-run\tverification\tPASS\t-\t-\n' \
    "$run_id" "$run_started_at" "$finished_at" >> "$action_manifest"
trap - EXIT HUP INT TERM
echo RUNTIME_REGRESSION_OK
