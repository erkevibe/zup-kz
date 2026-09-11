#!/bin/sh
set -eu

server_log=${ZUP_SERVER_LOG:-server.log}
server_jar=${ZUP_SERVER_JAR:-target/lsfusion-server-0.1.0-SNAPSHOT.jar}
http_port=${ZUP_TEST_HTTP_PORT:-7651}
rmi_port=${ZUP_TEST_RMI_PORT:-7652}
websocket_port=${ZUP_TEST_WEBSOCKET_PORT:-8887}
endpoint=${ZUP_TEST_ENDPOINT:-http://localhost:$http_port/exec}
admin_credentials=${ZUP_TEST_ADMIN_CREDENTIALS:-admin:ci-admin-only}
request_timeout=${ZUP_TEST_REQUEST_TIMEOUT:-600}
server_pid=

cleanup() {
    if [ -n "$server_pid" ]; then
        kill -TERM "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
}
trap cleanup EXIT HUP INT TERM

request_as() {
    credentials=$1
    action=$2
    output=$3
    curl --fail --silent --show-error --connect-timeout 10 \
        --max-time "$request_timeout" --user "$credentials" \
        "$endpoint?action=ZUPKZ.$action" --output "$output"
}

request() {
    request_as "$admin_credentials" "$1" "$2"
}

check() {
    action=$1
    output=$2
    assertion=$3
    request "$action" "$output"
    python3 "$assertion" "$output"
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

check initialRolePermissionsTest initial-role-permissions-result.json tests/assert_ui_role_setup.py
check payrollFormulaTest payroll-result.json tests/assert_payroll.py
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
request_as zup-access-time:zup-ui-test-only sameOrganizationTimekeeperMasterDataAttackTest \
    same-organization-timekeeper-master-data-attack-result.json
request_as zup-access-payroll:zup-ui-test-only sameOrganizationPayrollMasterDataAttackTest \
    same-organization-payroll-master-data-attack-result.json
request paymentAccountOverlapGuardTest payment-account-overlap-guard-result.json
request paymentAccountSecurityVerificationTest payment-account-security-verification-result.json
for action in employeeIinFormatGuardTest organizationBinFormatGuardTest bankDetailsFormatGuardTest; do
    request "$action" "$action-result.json"
done
python3 tests/assert_access_workflow.py \
    access-workflow-result.json cross-organization-policy-result.json \
    cross-organization-verification-result.json \
    payment-account-security-setup-result.json payment-account-overlap-guard-result.json \
    payment-account-security-verification-result.json \
    employeeIinFormatGuardTest-result.json organizationBinFormatGuardTest-result.json \
    bankDetailsFormatGuardTest-result.json

check uiRoleSetupTest ui-role-setup-result.json tests/assert_ui_role_setup.py
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
trap - EXIT HUP INT TERM
echo RUNTIME_REGRESSION_OK
