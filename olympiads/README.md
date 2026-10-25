# Архив математических олимпиад

Оригиналы общедоступных заданий и опубликованных решений сохраняются в `russia/`, `international/`, `university/`. Учтена только математика. Состав и состояние архива приведены в [проверяемом отчёте](../research/archive-resume-report-2026-10-25-round5.md).

Срез 25 октября 2026 после пятого прохода: **10154** уникальных математических документа по SHA-256, **4459** документов с классифицированными решениями/ответами. Все **11921** учитываемый файл прошли проверку SHA-256. В пятом проходе добавлено 17 файлов по новым ссылкам (11 новых SHA), решения/ответы впервые классифицированы для 18 уникальных документов. [Что восстановлено, ограничения комплектов и поиск зеркал MEMO](../research/archive-round5-notes-2026-10-25.md), [сверка по годам](../research/archive-year-reconciliation-2026-10-25-round5.md).

## Как найти материал

- Российские олимпиады: `russia/<олимпиада>/manifest.json`.
- Международные: `international/manifest.jsonl`.
- Студенческие: `university/manifest.jsonl`.
- Единая инвентаризация: `../research/archive-material-inventory-2026-10-25-round5.jsonl`.
- Недоступные документы и ошибки индексации: `../research/archive-continuation-queue-2026-10-25-round5.json`.

Запись `downloaded` означает сохранённый файл; запись о найденной ссылке сама по себе скачиванием не считается. У каждого сохранённого документа указан SHA-256. Годы, этапы и классы записаны там, где их удалось установить. Вторичные источники отмечены отдельно. Страницы архивов, административные документы и дополнительные статьи не включаются в число олимпиадных материалов.

## Воспроизведение

Запускать из корня репозитория:

```sh
python3 scripts/download_russia.py --max-pages 2400 --max-depth 6 --workers 8
python3 scripts/download_itmo_public.py
python3 scripts/download_international.py --contests APMO IMO EGMO BalticWay RMM MEMO BMO supplements SKMO society leader_reports verified_fallbacks
python3 scripts/download_university.py --resume
python3 scripts/download_partner_archives.py
python3 scripts/recover_archive_gaps.py
python3 scripts/audit_archive_metadata.py --contest rosatom --contest lomonosov --contest pvg --contest spbu --contest belchonok --contest bibn --contest verchenko --report research/archive-alternatives-metadata-audit-2026-10-23.json
python3 scripts/download_current_math_pages.py
python3 scripts/download_belchonok_current.py
python3 scripts/recover_round3_curated.py
python3 scripts/recover_bmo_mirrors.py
python3 scripts/recover_mathus_gap_years.py
python3 scripts/recover_turlom_official.py
python3 scripts/recover_round4_international.py
python3 scripts/recover_round4_russian_mirrors.py
python3 scripts/recover_round5_collections.py
python3 scripts/recover_round5_russian_solutions.py
python3 scripts/audit_round5_scans.py
python3 scripts/reconcile_archive_years.py --date 2026-10-25 --suffix round5
python3 scripts/summarize_archive_resume.py --date 2026-10-25 --suffix round5 --baseline research/archive-round5-baseline-2026-10-25.json
```

Не запускайте два процесса, записывающих один манифест. Большие оригиналы хранятся локально и исключены из Git; в Git сохраняются манифесты, скрипты и отчёты. Наличие материала за год не доказывает полноту всех вариантов и решений этого года. Полнота всех олимпиад за все годы пока не установлена.
