## Пример работы с rtsp потоком и обработки видеофайлов(сжатие и конвертация)

`git clone https://github.com/bekzod-fayzikuloff/rtsp_sample.git` <br>

* Установка зависимостей 
    * `pip install -r requirements.txt`
* Запуск скрипта записи RTSP потока 
    * `python rtsp.py --link[-l] <rstp_link>(ссылка) --duration[-d] <int|float>(длительность записи) --output[-o] <file_name>(названия файла для сохранения <необзятально>)`
* Запуск утилит для работы с видеофайлами(добавлена простой GUI для удобный работы)
    * `python convert.py`
