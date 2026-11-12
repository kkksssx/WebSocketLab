# Настройки веб-сервера
import os

HOST = ""            # "" = слушать на всех интерфейсах
PORT = 8080          # порт сервера (80 требует прав администратора)
BACKLOG = 5          # максимальная длина очереди входящих соединений
BUFFER_SIZE = 4096   # размер буфера приёма, байт
ENCODING = "utf-8"   # кодировка заголовков и текстовых сообщений
WWW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "www")
DEFAULT_FILE = "index.html"   # файл для запроса "/"
