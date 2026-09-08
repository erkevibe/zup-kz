# Эксплуатация ZUP-KZ

## Постоянный тестовый экземпляр

Сервер и web-клиент запускаются unit-файлами
`ops/systemd/zup-kz.service` и `ops/systemd/zup-kz-web.service`. Рабочий каталог
сервера не должен находиться в `/tmp`:

```text
/srv/zup-kz/
├── app/lsfusion-server.jar
├── bin/backup-db.sh
├── conf/settings.properties
└── logs/
```

Файл `conf/settings.properties` содержит пароль базы данных, принадлежит
пользователю `zupdev` и имеет права `0600`. Он не хранится в Git.

Проверка службы:

```bash
systemctl status zup-kz.service
systemctl status zup-kz-web.service
journalctl -u zup-kz.service -n 100 --no-pager
curl --fail --head http://127.0.0.1:8080/main
```

В production не включайте `settings.enableAPI=1`: произвольный `/eval` не нужен
пользователям ЗУП. Порт application server `7651` оставляйте доступным только
локально/в служебной сети; наружу публикуется web-клиент. Матрица ролей и
организационной области описана в [ACCESS_CONTROL.md](ACCESS_CONTROL.md).

## Резервное копирование

`zup-kz-backup.timer` ежедневно запускает логический дамп PostgreSQL от
локального пользователя `postgres`. Настройки находятся в файле
`/etc/default/zup-kz-backup`:

```bash
ZUP_DB_NAME=zup_ui_review_20260906
ZUP_BACKUP_DIR=/var/backups/zup-kz
ZUP_BACKUP_KEEP_DAYS=30
```

Скрипт сначала создаёт файл с суффиксом `.incomplete`, проверяет структуру
архива через `pg_restore --list` и только затем публикует готовый `.dump`.

Ручной запуск и проверка:

```bash
systemctl start zup-kz-backup.service
systemctl status zup-kz-backup.service
systemctl list-timers zup-kz-backup.timer
```

Не считайте резервирование проверенным, пока дамп не был восстановлен в
отдельную контрольную базу и приложение не прошло smoke-тест на ней.

## Проверка восстановления и обновления

`scripts/restore-drill.sh` восстанавливает указанный архив только в новую базу
с префиксом `zup_restore_drill_`, запускает на ней новый JAR на отдельных портах
и сверяет до/после запуска:

- количество строк и максимальный идентификатор во всех таблицах ZUP-KZ;
- суммы начислений, ИПН, социального налога, ОПВ и СО;
- успешное завершение обновления схемы и полный старт lsFusion.

Скрипт отказывается удалять или переиспользовать существующую базу. Контрольная
база удаляется после успешной или неуспешной проверки, если явно не задано
`ZUP_DRILL_KEEP_DB=1`.

Пример запуска на Debian-сервере:

```bash
sudo env \
  ZUP_DRILL_JAR=/srv/zup-kz/app/lsfusion-server.jar \
  ZUP_DRILL_SETTINGS=/srv/zup-kz/conf/settings.properties \
  ./scripts/restore-drill.sh \
  /var/backups/zup-kz/zup_ui_review_20260906-YYYYMMDDTHHMMSSZ.dump \
  zup_restore_drill_YYYYMMDD
```

Успешный результат заканчивается строкой `RESTORE_DRILL_OK` с SHA-256 дампа и
JAR, числом сверенных таблиц и временем старта. Эту строку прикладывают к
release notes. Проверка доказывает техническое восстановление и сохранность
контрольных итогов, но не заменяет юридическую сверку расчётов.
