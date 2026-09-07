#!/bin/sh
set -eu

: "${ZUP_DB_NAME:?Set ZUP_DB_NAME in /etc/default/zup-kz-backup}"

backup_dir=${ZUP_BACKUP_DIR:-/var/backups/zup-kz}
keep_days=${ZUP_BACKUP_KEEP_DAYS:-30}
stamp=$(date -u +%Y%m%dT%H%M%SZ)
archive="$backup_dir/$ZUP_DB_NAME-$stamp.dump"
temporary="$archive.incomplete"

umask 077
mkdir -p "$backup_dir"
trap 'rm -f "$temporary"' EXIT HUP INT TERM

pg_dump --format=custom --dbname="$ZUP_DB_NAME" --file="$temporary"
pg_restore --list "$temporary" >/dev/null
mv "$temporary" "$archive"
find "$backup_dir" -maxdepth 1 -type f \
    -name "$ZUP_DB_NAME-*.dump" -mtime "+$keep_days" -delete

printf '%s\n' "$archive"
