from urllib.parse import quote
import requests

class Cataas:
    base_url = 'https://cataas.com'

    def get_image(self, text: str) -> bytes:
        encoded_text = quote(text, safe='')
        url = f'{self.base_url}/cat/says/{encoded_text}'

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.content


