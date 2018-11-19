from .Dataset import Dataset
import io
import logging
import re
from urllib.request import urlopen
import zipfile

logger = logging.getLogger(__name__)


def get_png_from_zip(zip):
    zip_data = io.BytesIO()
    zip_data.write(zip)
    zip_file = zipfile.ZipFile(zip_data)

    name = ""
    for n in zip_file.namelist():
        if re.match(r"2x/.*\.png", n):
            name = n

    image = zip_file.open(name)
    return image.read()


class DatasetMaterialIcons(Dataset):
    base_url_styles = "https://storage.googleapis.com/non-spec-apps/mio-icons/latest/{}.css"
    base_url_png = "https://material.io/tools/icons/static/icons/{}-black-48.zip"
    base_url_svg = "https://material.io/tools/icons/static/icons/{}-24px.svg"

    def __init__(self):
        self.styles = [
            "baseline",
            "sharp",
            "outline",
            "round",
            "twotone"
        ]
        self.style_idx = 0

        self.icons = []
        self.icon_idx = 0
        super(DatasetMaterialIcons, self).__init__('MaterialIcons')

    def _get_next_icons(self):
        style = ''

        try:
            style = self.styles[self.style_idx]
            self.style_idx += 1

            with urlopen(self.base_url_styles.format(style)) as resp:
                stylesheet = resp.read().decode('utf-8')
                self.icons = re.findall(r'\.(.*) {', stylesheet)
                self._log("Fetched icons of style {}: {} icons found".format(style, len(self.icons)))

        except IndexError:
            self._log("No more icons")
            self.icons = None
        except Exception as e:
            self._log("Error fetching {}: {}".format(style, e))
            self._get_next_icons()

        self.icon_idx = 0

    def get_image_urls(self, amount):
        result = []

        to_add = amount
        while len(result) < amount:
            if self.icons is None:
                break

            new_icons = self.icons[self.icon_idx:self.icon_idx + to_add]
            to_add -= len(new_icons)
            self.icon_idx += len(new_icons)

            result += [
                (
                    '{}-{}'.format(self.name, icon),
                    self.base_url_png.format(icon),
                    self.base_url_svg.format(icon),
                    get_png_from_zip,
                    None
                )
                for icon in new_icons
            ]

            if len(result) < amount:
                self._get_next_icons()

        return result

    def __getstate__(self):
        return {
            'icons': self.icons,
            'icon_idx': self.icon_idx,
            'styles': self.styles,
            'style_idx': self.style_idx
        }
