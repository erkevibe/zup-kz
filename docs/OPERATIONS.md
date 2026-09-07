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
