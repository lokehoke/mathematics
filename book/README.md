# Ресурсы книги

| Папка | Что внутри |
| --- | --- |
| [source/](source/) | Рукопись LaTeX и все необходимые ресурсы |
| [tools/](tools/) | Сборка, генерация графиков и проверки |
| [references/](references/) | Проверки книги, сверка с экзаменами и источники выбранных задач |

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

Данные из `source/data/` — основа для генерации глав. Изменения следует вносить туда и в инструменты сборки, чтобы повторная генерация их сохранила. Тексты задач и источники олимпиадной подборки находятся в `source/data/olympiad-selected.json`.

[Итоговая проверка книги](references/review-edition11-final-2026-10-25.md). Проверка оригиналов олимпиадных задач требует локального архива `olympiads/`; сам архив и его каталог в Git не входят.
