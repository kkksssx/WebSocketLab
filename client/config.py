# Настройки тестового клиента
SERVER_NAME = "127.0.0.1"   # IP-адрес или имя хоста веб-сервера
SERVER_PORT = 8080
BUFFER_SIZE = 4096
ENCODING = "utf-8"
# Три HTTP-запроса для проверки: два успешных и один на несуществующий файл
PATHS = ["/index.html", "/about.html", "/missing.html"]
