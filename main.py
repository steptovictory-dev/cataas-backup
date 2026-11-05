import requests
import os
import json

from time import sleep
from urllib.parse import quote
from getpass import getpass
from dotenv import load_dotenv  

token = os.getenv('TOKEN')

class Cataas:
    base_url = 'https://cataas.com'

    def get_image(self, text: str) -> bytes:
        encoded_text = quote(text, safe='')
        url = f'{self.base_url}/cat/says/{encoded_text}'

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.content

class YandexDisk:
    base_url = 'https://cloud-api.yandex.net'

    def __init__(self, token: str):
        self.headers = {'Authorization': f'OAuth {token}'}

    def create_folder(self, folder_path: str) -> None:
        response = requests.put(f'{self.base_url}/v1/disk/resources', 
                headers=self.headers, 
                params={'path': folder_path},
                timeout=15,
        )
        response.raise_for_status()

    def upload_from_url(self, image_url: str, disk_path: str) -> dict:
        response = requests.post(f'{self.base_url}/v1/disk/resources/upload', 
                headers=self.headers, 
                params={'url': image_url, 'path': disk_path},
                timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def wait_for_upload(self, operation_url: str) -> None:
        for _ in range(20):  
            response = requests.get(operation_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            status = response.json()['status']

            if status == 'success':
                return
            elif status == 'failed':
                raise SystemExit('Ошибка загрузки файла на Яндекс.Диск') 

            sleep(1)

        raise TimeoutError('Превышено время ожидания загрузки файла')

    def get_file_size(self, disk_path: str) -> int:
        response = requests.get(f'{self.base_url}/v1/disk/resources', 
                headers=self.headers, 
                params={'path': disk_path},
                timeout=15,
        )
        response.raise_for_status()
        return response.json()['size']  



if __name__ == '__main__':
    load_dotenv()  

    token = os.getenv('TOKEN', '').strip()
    if not token:
        token = getpass('Введите токен Яндекс.Диска: ').strip()
    
    if not token:
        raise SystemExit('Токен не указан')

    disk = YandexDisk(token)
    # disk.create_folder('AIEPYAPI-162')  # создаем папку по названию группы 
    # print('Папка создана')

    text = input('Введите текст для надписи на картинке: ').strip()
    if not text:
        raise SystemExit('Текст не указан')

    encoded_text = quote(text, safe='')
    image_url = f'{Cataas.base_url}/cat/says/{encoded_text}'
    disk_path = f'AIEPYAPI-162/{text}.jpg'
    
    result = disk.upload_from_url(image_url, disk_path)

    disk.wait_for_upload(result['href'])
    size = disk.get_file_size(disk_path)

    report = [{'file_name': f'{text}.jpg', 'size': size}]
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    print('картинка загружена на Яндекс Диск, отчет сохранен в result.json')