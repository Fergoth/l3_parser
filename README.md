# Утилита для скачивания книг с tululu.org

Утилита позволяет скачивать книги с https://tululu.org


## Запуск

Для запуска утилиты у вас уже должен быть установлен Python 3.

- Скачайте код
- Установите зависимости командой
```
pip install -r requirements.txt
```
- Запустите скрипт для скачивания книг по айди командой
```
python download_books_by_id.py 5 10
```
- Обязательные параметры `start_id` и `end_id ` диапазон скачиваемых книг(`end_id` не включая), где `id`
номер книг. Например `id = 1` https://tululu.org/b1/

После чего в папке откуда запускается скрипт, у вас появится две папки `\books` и `\images` в которые загрузятся
книги и обложки к книгам соответственно

Так же доступен  скрипт для постраничного скачивания книг с фантастикой
https://tululu.org/l55/
Помимо картинок и текста добавлено описание скачанных книг
```
python parse_tululu_category.py
```

Доступны следующие параметры для скрипта
- --start_page --end_page, Скачивают книги cо страниц [start_page;end_page).
Значения по умолчанию 1,2
```
python parse_tululu_category.py --start_page 10 --end_page 11
```
- --folder.(по умолчанию downloaded) Позволяет указать директорию в которой создадутся директории для картинок,txt, и описания книг.
```
python parse_tululu_category.py --folder some_folder
```
- --skip_imgs. Флаг отключающий скачивание картинок.
- --skip_txt. Флаг отключающий скачивание книг.
Пример скрипта который скачает только описания книг
```
python parse_tululu_category.py --skip_img --skip_txt
```


Так же доступен пример со скачанными книгами в виде GitHub pages.
Сайт доступен по [ссылке](https://fergoth.github.io/l3_parser/pages/index1.html)

Для локального запуска сайта запустить скрипт:
```commandline
python render_website.py [путь до файла description.json]
```
По умолчанию путь media/description.json и скрипт запустит сайт с готовыми данными как на GutHub pages по адресу http://127.0.0.1:5500/pages/index1.html.

Для запуска со своими книгами, требуется удалить папку pages, запустить скрипт parse_tululu_category.py и явно указать путь к description.json (по умолчанию downloaded/description.json)
## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
