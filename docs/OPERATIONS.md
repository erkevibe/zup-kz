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

## Наблюдение за журналами

`zup-kz-observer.service` непрерывно читает весь journald хоста и прикладные журналы,
фиксирует позицию каждого источника в SQLite и группирует одинаковые ошибки в
инциденты. SQLite находится вне PostgreSQL приложения, поэтому наблюдение не
прекращается при падении основной БД. Сырые сообщения очищаются от паролей,
токенов, ИИН и IBAN до записи.

Установка на `zup-dev`:

```bash
sudo useradd --system --home /var/lib/zup-observer --create-home zupobserver
sudo install -d -m 0750 -o root -g zupobserver /opt/zup-observer
sudo install -m 0755 ops/observer/zup_observer.py /opt/zup-observer/
sudo install -m 0640 -o root -g zupobserver ops/observer/rules.json /etc/zup-observer.json
sudo install -m 0644 conf/observer.env.example /etc/default/zup-observer
sudo install -m 0644 ops/systemd/zup-kz-observer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now zup-kz-observer.service
```

Пользователю `zupobserver` выдаётся только чтение конкретных каталогов логов;
доступ к конфигурации приложения и паролям БД не нужен. Проверка:

```bash
systemctl status zup-kz-observer.service
sudo -u zupobserver /usr/bin/python3 /opt/zup-observer/zup_observer.py report \
  --config /etc/zup-observer.json
```

На Guacamole запускается отдельный локальный экземпляр по unit-файлу
`zup-kz-observer-guacamole.service` и конфигурации `rules.guacamole.json`.
Он читает journald и `docker logs` на том же LXC; сырые логи и ключи между
серверами не передаются. Сервис запускается от root, потому что доступ к Docker
socket фактически равносилен root, но ограничен systemd hardening и имеет право
записи только в `/var/lib/zup-observer`. ИИ-наблюдатель получает с каждого LXC
только результат команды `zup_observer.py report` через уже настроенный
административный канал.

Сообщение вида
`ZUP_PROCESS process=payroll case=RUN-1 activity=calculated organization=ORG-1`
создаёт событие мини-process-mining. Допустимые старты и переходы кадрового,
согласовательного и зарплатного процессов заданы в `rules.json`. Нарушение
порядка становится отдельным инцидентом. Новые инциденты пишутся в
`/var/lib/zup-observer/alerts.ndjson`; периодический ИИ-наблюдатель читает этот
обезличенный поток, а не исходные журналы.

Модуль `PayrollProcessEvents` автоматически пишет такие события при сборе
табеля, расчёте зарплаты, утверждении социальных платежей, налогов и взысканий,
закрытии расчёта, утверждении ведомости и выплате. В события не попадают Ф.И.О.
работников и денежные суммы. В `report` доступны текущие этапы и фактические
переходы процессов. Если документ остаётся на этапе дольше срока из
`max_age_seconds`, создаётся один `WARN` с рекомендацией следующего штатного
действия; после продолжения процесса предупреждение закрывается автоматически.
Одна запись, попавшая одновременно в файл приложения и journald, считается
одним процессным событием в пределах `dedupe_seconds`; исходные строки журналов
при этом сохраняются обе. Первый обнаруженный этап уже начатого до установки
расчёта принимается как исходное состояние, а последующие переходы проверяются.

Наблюдатель не меняет кадровые и денежные документы. Автоматически допустимо
восстанавливать только сам сервис наблюдения; перезапуск ZUP-KZ, изменение БД
или проведение документов требуют решения оператора.

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
