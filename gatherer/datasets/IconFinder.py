from .Dataset import Dataset
from html.parser import HTMLParser
from urllib.request import urlopen


def get_attr(name, attrs):
    attr = [el for el in attrs if el[0] == name]
    if len(attr):
        return attr[0][1]

    return None


class IconsetBrowerHTMLParser(HTMLParser):
    def __init__(self):
        super(IconsetBrowerHTMLParser, self).__init__()
        self.is_looking_for_link = False
        self.found_iconsets = []

    def handle_starttag(self, tag, attrs):
        el_class = get_attr("class", attrs)
        if el_class:
            if "iconset-preview" in el_class:
                self.is_looking_for_link = True
                return

        if self.is_looking_for_link and tag == "a":
            href = get_attr("href", attrs)
            if href:
                self.found_iconsets.append(href)
                self.is_looking_for_link = False

    def get_iconsets(self):
        return self.found_iconsets


class IconsetHTMLParser(HTMLParser):
    def __init__(self):
        super(IconsetHTMLParser, self).__init__()
        self.found_icons = []

    def handle_starttag(self, tag, attrs):
        el_class = get_attr("class", attrs)
        if el_class:
            if "icon-preview" in el_class:
                data_id = get_attr("data-asset-id", attrs)
                if data_id:
                    self.found_icons.append(data_id)

    def get_icons(self):
        return self.found_icons


class DatasetIconFinder(Dataset):
    base_url = "https://www.iconfinder.com{}"
    base_url_iconsets = base_url.format("/icon-sets/featured/free/{}")
    base_url_png = base_url.format("/icons/{}/download/png/128")
    base_url_svg = base_url.format("/icons/{}/download/svg/128")

    def __init__(self):
        self.search_idx = 0

        self.iconsets = []
        self.iconset_idx = 0

        self.icons = []
        self.icon_idx = 0
        super(DatasetIconFinder, self).__init__('IconFinder')

    def _get_next_iconsets(self):
        try:
            print(self.base_url_iconsets.format(str(self.search_idx)))
            with urlopen(self.base_url_iconsets.format(str(self.search_idx))) as resp:
                parser = IconsetBrowerHTMLParser()
                parser.feed(resp.read().decode('utf-8'))

                self.iconsets = parser.get_iconsets()

                self._log("Fetched next iconsets ({}): {} sets found".format(self.search_idx, len(self.iconsets)))

                if len(self.iconsets) == 0:
                    self._log("No more iconsets")
                    self.iconsets = None

            self.search_idx += 1

        except Exception as e:
            self._log("Error fetching iconsets ({}): {}".format(self.search_idx, e))
            self.search_idx += 1
            self._get_next_iconsets()

        self.iconset_idx = 0

        return len(self.iconsets)

    def _get_next_icons(self):
        if self.iconsets is None:
            if self.icons:
                self._log("No more icons")
                self.icons = None

            return

        iconset = ''

        try:
            iconset = self.iconsets[self.iconset_idx]
            self.iconset_idx += 1

            with urlopen(self.base_url.format(iconset)) as resp:
                parser = IconsetHTMLParser()
                parser.feed(resp.read().decode('utf-8'))

                self.icons = parser.get_icons()

                self._log("Fetched icons of iconset {}: {} icons found".format(iconset, len(self.icons)))

        except IndexError:
            self._get_next_iconsets()
            self._get_next_icons()

        except Exception as e:
            self._log("Error fetching {}: {}".format(iconset, e))
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
                    None,
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
            'iconsets': self.iconsets,
            'iconsets_idx': self.iconset_idx,
            'search_idx': self.search_idx
        }
