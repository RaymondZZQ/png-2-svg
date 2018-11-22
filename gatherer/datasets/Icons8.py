from .Dataset import Dataset
import json
from urllib.request import urlopen


class DatasetIcons8 (Dataset):
    base_url = "https://api.icons8.com/api/iconsets/v4/latest?category=free_icons&amount={}&offset={}"
    base_url_png = "https://image.icons8.com/?id={}&format=png&size=500&color=000000"
    #base_url_svg = "https://api.icons8.com/api/iconsets/download?id={}&format=svg.editable&size=100&color=000000"
    base_url_svg = "https://api.icons8.com/api/iconsets/download?id={}&format=svg.simplified&size=100&color=000000"

    def __init__(self):
        self.offset = 0
        super(DatasetIcons8, self).__init__('Icons8')

    def get_image_urls(self, amount):
        url = self.base_url.format(amount, self.offset)

        self._log('Fetching icons ({})'.format(url))

        with urlopen(url) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        self.offset += amount

        return [
            (
                '{}-{}'.format(self.name, icon['name']),
                self.base_url_png.format(icon['id']),
                self.base_url_svg.format(icon['id']),
                None,
                None
            )
            for icon in data['icons']
        ]

    def __getstate__(self):
        return {
            'offset': self.offset
        }