# Ресурсы книги

| Папка | Что внутри |
| --- | --- |
| [source/](source/) | Рукопись LaTeX и все необходимые ресурсы |
| [tools/](tools/) | Скрипты, необходимые для сборки и проверки вёрстки |

Основной файл — [source/main.tex](source/main.tex). Главы находятся в `source/chapters/`, иллюстрации — в `source/images/`, шрифты — в `source/fonts/`. Исходные данные для сборки глав и задач — в `source/data/`; порядок чтения задаёт `source/data/book-structure.json`.

## Сборка

Из корня репозитория:

```sh
python3 book/tools/build_book.py
```

Нужны Python с Pillow, pdfplumber и pypdf, а также Tectonic. Ghostscript создаёт компактный PDF для чтения. Результат появится в `rendered/algebra-for-beloved-kitten.pdf`.

Готовый `source/main.tex` также можно собрать непосредственно в папке `book/source/`:

```sh
tectonic --keep-logs --keep-intermediates main.tex
```

Данные из `source/data/` — основа для генерации глав. Изменения следует вносить туда и в инструменты сборки, чтобы повторная генерация их сохранила. Условия, ответы и решения олимпиадной подборки находятся в `source/data/olympiad-selected.json`, ссылки на первоисточники — в `source/data/olympiad-sources.json`.

Сборка создаёт промежуточные `source/book-data.json` и `source/cats-flow.json`, а отчёты — в `book/.work/reports/`. Эти файлы исключены из Git. Ранее полученные рабочие отчёты и выгрузки экзаменов сохраняются только локально в `book/references/`. Архив олимпиад и его каталог также остаются локально; для сборки книги они не нужны.
