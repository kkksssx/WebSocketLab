# Тестовый клиент: отправляет несколько HTTP-запросов серверу и печатает ответы
import sys
from socket import socket, AF_INET, SOCK_STREAM

import config


def http_get(path):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((config.SERVER_NAME, config.SERVER_PORT))
    request = (f"GET {path} HTTP/1.1\r\n"
               f"Host: {config.SERVER_NAME}:{config.SERVER_PORT}\r\n"
               f"Connection: close\r\n\r\n")
    clientSocket.sendall(request.encode(config.ENCODING))
    data = b""
    while True:                       # читаем до закрытия соединения сервером
        chunk = clientSocket.recv(config.BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
    clientSocket.close()
    return data


def main():
    paths = sys.argv[1:] or config.PATHS
    for n, path in enumerate(paths, 1):
        print(f"=== Запрос {n}: GET {path} ===")
        data = http_get(path)
        head, _, body = data.partition(b"\r\n\r\n")
        print(head.decode(config.ENCODING, errors="replace").replace("\r\n", "\n"))
        print(f"[тело ответа: {len(body)} байт]")
        preview = body.decode(config.ENCODING, errors="replace")[:200]
        if "\x00" not in preview:
            print(preview.strip())
        print()


if __name__ == "__main__":
    main()
