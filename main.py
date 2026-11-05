import requests
import os

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

if __name__ == '__main__':
    load_dotenv()  

    token = os.getenv('TOKEN', '').strip()
    if not token:
        token = getpass('Введите токен Яндекс.Диска: ').strip()
    
    if not token:
        raise SystemExit('Токен не указан')

    disk = YandexDisk(token)
    disk.create_folder('AIEPYAPI-162')  # создаем папку по названию группы 
    print('Папка создана')
