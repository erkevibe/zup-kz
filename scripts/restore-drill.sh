#!/bin/sh
set -eu

usage() {
    echo "Usage: ZUP_DRILL_JAR=... ZUP_DRILL_SETTINGS=... $0 DUMP TARGET_DB" >&2
    exit 2
}

fail() {
    echo "restore drill failed: $*" >&2
    exit 1
}

[ "$#" -eq 2 ] || usage
[ "$(id -u)" -eq 0 ] || fail "run as root"

dump=$1
target_db=$2
: "${ZUP_DRILL_JAR:?Set ZUP_DRILL_JAR to the new application JAR}"
: "${ZUP_DRILL_SETTINGS:?Set ZUP_DRILL_SETTINGS to a working settings.properties}"

case "$target_db" in
    zup_restore_drill_*) ;;
    *) fail "TARGET_DB must start with zup_restore_drill_" ;;
esac
case "$target_db" in
    *[!a-zA-Z0-9_]*) fail "TARGET_DB contains unsupported characters" ;;
esac

[ -r "$dump" ] || fail "dump is not readable: $dump"
[ -r "$ZUP_DRILL_JAR" ] || fail "application JAR is not readable"
[ -r "$ZUP_DRILL_SETTINGS" ] || fail "settings file is not readable"

app_user=${ZUP_DRILL_APP_USER:-zupdev}
db_owner=${ZUP_DRILL_DB_OWNER:-zup_kz_app}
http_port=${ZUP_DRILL_HTTP_PORT:-7661}
rmi_port=${ZUP_DRILL_RMI_PORT:-7662}
timeout=${ZUP_DRILL_TIMEOUT_SECONDS:-300}
keep_db=${ZUP_DRILL_KEEP_DB:-0}

for command_name in createdb dropdb pg_restore psql runuser java sha256sum; do
    command -v "$command_name" >/dev/null 2>&1 || fail "missing command: $command_name"
done
id "$app_user" >/dev/null 2>&1 || fail "unknown application user: $app_user"

if runuser -u postgres -- psql -Atqc \
    "SELECT 1 FROM pg_database WHERE datname = '$target_db'" | grep -q 1; then
    fail "target database already exists: $target_db"
fi

temporary=$(mktemp -d /tmp/zup-restore-drill.XXXXXX)
runtime=$temporary/runtime
server_log=$temporary/server.log
before_manifest=$temporary/before.manifest
after_manifest=$temporary/after.manifest
created=0
server_pid=

app_group=$(id -gn "$app_user")
chown "$app_user:$app_group" "$temporary"

cleanup() {
    if [ -n "$server_pid" ] && kill -0 "$server_pid" 2>/dev/null; then
        kill -TERM "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
    if [ "$created" -eq 1 ] && [ "$keep_db" != 1 ]; then
        runuser -u postgres -- dropdb --if-exists "$target_db" >/dev/null
    fi
    rm -rf "$temporary"
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM

database_manifest() {
    database=$1
    output=$2
    : > "$output"

    runuser -u postgres -- psql -v ON_ERROR_STOP=1 -Atq -d "$database" -c \
        "SELECT tablename FROM pg_tables
         WHERE schemaname = 'public' AND tablename LIKE '_auto_zupkz_%'
         ORDER BY tablename" |
    while IFS= read -r table_name; do
        row_count=$(runuser -u postgres -- psql -v ON_ERROR_STOP=1 -Atq \
            -d "$database" -c "SELECT count(*) FROM \"$table_name\"")
        max_key=$(runuser -u postgres -- psql -v ON_ERROR_STOP=1 -Atq \
            -d "$database" -c "SELECT COALESCE(max(key0), 0) FROM \"$table_name\"")
        printf 'table|%s|rows=%s|max_key=%s\n' \
            "$table_name" "$row_count" "$max_key" >> "$output"
    done

    runuser -u postgres -- psql -v ON_ERROR_STOP=1 -Atq -d "$database" -c \
        "SELECT 'metric|payroll_amount|value=' ||
                    COALESCE(sum(zupkz_calculationamount_payrollline), 0)
           FROM _auto_zupkz_payrollline
         UNION ALL
         SELECT 'metric|ipn_amount|value=' ||
                    COALESCE(sum(zupkz_ipnamount_taxcalculationline), 0)
           FROM _auto_zupkz_taxcalculationline
         UNION ALL
         SELECT 'metric|social_tax_amount|value=' ||
                    COALESCE(sum(zupkz_socialtaxamount_taxcalculationline), 0)
           FROM _auto_zupkz_taxcalculationline
         UNION ALL
         SELECT 'metric|opv_amount|value=' ||
                    COALESCE(sum(zupkz_opvamount_socialpaymentline), 0)
           FROM _auto_zupkz_socialpaymentline
         UNION ALL
         SELECT 'metric|so_amount|value=' ||
                    COALESCE(sum(zupkz_soamount_socialpaymentline), 0)
           FROM _auto_zupkz_socialpaymentline
         ORDER BY 1" >> "$output"
}

pg_restore --list "$dump" >/dev/null
runuser -u postgres -- createdb --owner="$db_owner" "$target_db"
created=1
runuser -u postgres -- pg_restore --exit-on-error --no-owner --no-privileges \
    --role="$db_owner" --dbname="$target_db" "$dump"

database_manifest "$target_db" "$before_manifest"

install -d -m 0700 -o "$app_user" -g "$app_group" "$runtime" "$runtime/conf"
sed "s/^db.name=.*/db.name=$target_db/" "$ZUP_DRILL_SETTINGS" > "$runtime/conf/settings.properties"
if ! grep -q '^db.name=' "$runtime/conf/settings.properties"; then
    printf '\ndb.name=%s\n' "$target_db" >> "$runtime/conf/settings.properties"
fi
chown "$app_user:$app_group" "$runtime/conf/settings.properties"
chmod 0600 "$runtime/conf/settings.properties"

(
    cd "$runtime"
    exec runuser -u "$app_user" -- java -Xms256m -Xmx2g \
        -Dhttp.port="$http_port" -Drmi.port="$rmi_port" \
        -jar "$ZUP_DRILL_JAR"
) > "$server_log" 2>&1 &
server_pid=$!

elapsed=0
while ! grep -q 'Server has successfully started' "$server_log"; do
    if ! kill -0 "$server_pid" 2>/dev/null; then
        tail -100 "$server_log" >&2
        fail "application stopped during restored-database startup"
    fi
    if [ "$elapsed" -ge "$timeout" ]; then
        tail -100 "$server_log" >&2
        fail "application startup exceeded ${timeout}s"
    fi
    sleep 1
    elapsed=$((elapsed + 1))
done

kill -TERM "$server_pid" 2>/dev/null || true
wait "$server_pid" 2>/dev/null || true
server_pid=

database_manifest "$target_db" "$after_manifest"
if ! diff -u "$before_manifest" "$after_manifest"; then
    fail "business row counts, identifiers, or control totals changed during startup"
fi

table_count=$(grep -c '^table|' "$after_manifest")
dump_hash=$(sha256sum "$dump" | cut -d ' ' -f1)
jar_hash=$(sha256sum "$ZUP_DRILL_JAR" | cut -d ' ' -f1)
printf 'RESTORE_DRILL_OK database=%s tables=%s startup_seconds=%s dump_sha256=%s jar_sha256=%s\n' \
    "$target_db" "$table_count" "$elapsed" "$dump_hash" "$jar_hash"
