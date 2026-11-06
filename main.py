import os
import json
import logging
from getpass import getpass
from time import sleep
from urllib.parse import quote

import requests
from dotenv import load_dotenv


class Cataas:
    """Формирует ссылку на картинку котиков с заданной надписью."""

    base_url = 'https://cataas.com'

    def get_image_url(self, text: str) -> str:
        # Кодируем надпись, чтобы не сломать URL
        encoded_text = quote(text, safe='')
        return f'{self.base_url}/cat/says/{encoded_text}'


class YandexDisk:
    """
    Класс для работы с Яндекс.Диском через API.
    Создает папку, загружает картинку по ссылке и получает её размер.
    """

    base_url = 'https://cloud-api.yandex.net'

    def __init__(self, token: str):
        self.headers = {'Authorization': f'OAuth {token}'}

    def create_folder(self, folder_path: str) -> bool:
        response = requests.put(
            f'{self.base_url}/v1/disk/resources',
            headers=self.headers,
            params={'path': folder_path},
            timeout=15,
        )

        # 409 = Conflict. Проверяем, что папка уже существует
        if response.status_code == 409:
            return (
                response.json().get('error')
                == 'DiskPathPointsToExistentDirectoryError'
            )

        # 201 = Created. Папка успешно создана
        return response.status_code in {201, 409}

    def upload_from_url(self, image_url: str, disk_path: str) -> dict:
        response = requests.post(
            f'{self.base_url}/v1/disk/resources/upload',
            headers=self.headers,
            params={'url': image_url, 'path': disk_path},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def wait_for_upload(self, operation_url: str) -> None:
        for _ in range(20):
            response = requests.get(
                operation_url,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            status = response.json()['status']

            if status == 'success':
                return
            elif status == 'failed':
                raise SystemExit('Ошибка загрузки файла на Яндекс.Диск')

            sleep(1)

        raise TimeoutError('Превышено время ожидания загрузки файла')

    def get_file_size(self, disk_path: str) -> int:
        response = requests.get(
            f'{self.base_url}/v1/disk/resources',
            headers=self.headers,
            params={'path': disk_path},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()['size']


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    load_dotenv()

    token = os.getenv('TOKEN', '').strip()
    if not token:
        token = getpass('Введите токен Яндекс.Диска: ').strip()

    if not token:
        raise SystemExit('Токен не указан')

    disk = YandexDisk(token)
    folder_name = 'AIEPYAPI-162'    # имя папки по номеру группы

    if not disk.create_folder(folder_name):
        raise SystemExit('Не удалось создать папку на Яндекс.Диске')

    logging.info('Папка на Яндекс.Диске готова')

    text = input('Введите текст для надписи на картинке: ').strip()
    if not text:
        raise SystemExit('Текст не указан')

    cataas = Cataas()
    image_url = cataas.get_image_url(text)
    disk_path = f'{folder_name}/{text}.jpg'

    logging.info(f'Загрузка картинки с надписью "{text}" на Яндекс.Диск...')
    result = disk.upload_from_url(image_url, disk_path)

    # Ждем завершения загрузки файла на Яндекс.Диск
    disk.wait_for_upload(result['href'])
    size = disk.get_file_size(disk_path)

    report = [{'file_name': f'{text}.jpg', 'size': size}]
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    logging.info('Картинка загружена на Яндекс Диск, отчет сохранен в result.json')


if __name__ == '__main__':
    main()