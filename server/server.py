# Лабораторная работа №5, вариант 1: простой веб-сервер на сокетах (TCP)
import mimetypes
import os
from datetime import datetime, timezone
from email.utils import format_datetime
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from urllib.parse import unquote, urlsplit

import config

REASONS = {200: "OK", 400: "Bad Request", 403: "Forbidden",
           404: "Not Found", 405: "Method Not Allowed"}


def build_response(code, body=b"", content_type="text/html; charset=utf-8"):
    """Формирует HTTP-ответ: строка статуса + заголовки + пустая строка + тело."""
    headers = [
        f"HTTP/1.1 {code} {REASONS[code]}",
        f"Date: {format_datetime(datetime.now(timezone.utc), usegmt=True)}",
        "Server: AIPOS-Lab5/1.0",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
    ]
    if code == 405:
        headers.append("Allow: GET")
    return ("\r\n".join(headers) + "\r\n\r\n").encode(config.ENCODING) + body


def error_page(code):
    text = f"<html><head><meta charset='utf-8'><title>{code} {REASONS[code]}</title></head>" \
           f"<body><h1>{code} {REASONS[code]}</h1></body></html>"
    return build_response(code, text.encode(config.ENCODING))


def read_request(conn):
    """Читает из сокета данные до конца заголовков (пустая строка)."""
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(config.BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
        if len(data) > 65536:   # защита от слишком больших заголовков
            break
    return data.decode(config.ENCODING, errors="replace")


def resolve_path(url_path):
    """Преобразует путь из URL в путь к файлу внутри WWW_DIR (None — выход за пределы каталога)."""
    path = unquote(urlsplit(url_path).path)
    if path.endswith("/"):
        path += config.DEFAULT_FILE
    full = os.path.realpath(os.path.join(config.WWW_DIR, path.lstrip("/")))
    root = os.path.realpath(config.WWW_DIR)
    if full != root and not full.startswith(root + os.sep):
        return None
    return full


def handle_request(message):
    """Разбирает HTTP-запрос и возвращает готовый ответ (bytes)."""
    lines = message.split("\r\n")
    parts = lines[0].split()
    if len(parts) != 3 or not parts[2].startswith("HTTP/"):
        return error_page(400)
    method, url, _version = parts
    if method != "GET":
        return error_page(405)
    full = resolve_path(url)
    if full is None:
        return error_page(403)
    try:
        with open(full, "rb") as f:          # IOError, если файла нет
            body = f.read()
    except (IOError, OSError):
        return error_page(404)
    ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
    if ctype.startswith("text/"):
        ctype += f"; charset={config.ENCODING}"
    return build_response(200, body, ctype)


def main():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind((config.HOST, config.PORT))
    serverSocket.listen(config.BACKLOG)
    print(f"Сервер запущен: http://127.0.0.1:{config.PORT}/  (каталог: {config.WWW_DIR})", flush=True)
    try:
        while True:
            print("Готов к обслуживанию...", flush=True)
            connectionSocket, addr = serverSocket.accept()
            try:
                message = read_request(connectionSocket)
                request_line = message.split("\r\n")[0]
                response = handle_request(message)
                status = response.split(b"\r\n", 1)[0].decode()
                print(f"{addr[0]}:{addr[1]}  \"{request_line}\"  ->  {status}", flush=True)
                connectionSocket.sendall(response)
            except Exception as e:        # ошибка одного клиента не должна ронять сервер
                print("Ошибка при обработке клиента:", e, flush=True)
            finally:
                connectionSocket.close()
    except KeyboardInterrupt:
        print("\nОстановка сервера.")
    finally:
        serverSocket.close()


if __name__ == "__main__":
    main()
