from io import BytesIO
import logging
from pathlib import Path
from PIL import Image
import queue
import threading
import time
from urllib.request import urlopen

from datasets.Icons8 import DatasetIcon8
from datasets.MaterialIcons import DatasetMaterialIcons

MAX_DOWNLOADS = 10

logger = logging.getLogger(__name__)


def rescale(size, data):
    result = BytesIO()
    image = Image.open(BytesIO(data))
    image.resize((size, size)).save(result, "PNG")
    return result.getbuffer()


def no_transform(el):
    return el


class ImageDownloader(threading.Thread):
    def __init__(self, id, url_queue, directory):
        threading.Thread.__init__(self)
        self.id = id
        self.queue = url_queue
        self.directory = directory

    def run(self):
        while True:
            (name, url_png, url_svg, png_trans, svg_trans) = self.queue.get()

            if png_trans is None:
                png_trans = no_transform
            if svg_trans is None:
                svg_trans = no_transform

            try:
                # download png
                download_path = self.directory / 'png' / '{}.png'.format(name)
                with urlopen(url_png, timeout=5) as image, download_path.open('wb') as f:
                    f.write(rescale(128, png_trans(image.read())))

                # download svg
                download_path = self.directory / 'svg' / '{}.svg'.format(name)
                with urlopen(url_svg, timeout=5) as image, download_path.open('w') as f:
                    f.write(svg_trans(image.read()).decode('utf-8'))
            except Exception as e:
                logger.info("Error downloading {}: {}".format(name, e))
            finally:
                logger.info("Downloaded image {} ({})({})".format(name, url_png, url_svg))
                self.queue.task_done()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(relativeCreated)6d %(threadName)s %(message)s')

    url_queue = queue.Queue()
    datasets = [
        DatasetMaterialIcons(),
        DatasetIcon8()
    ]

    download_dir = Path('../dataset')
    if not download_dir.exists():
        download_dir.mkdir()

    download_threads = []
    for i in range(10):
        thread = ImageDownloader(i, url_queue, download_dir)
        thread.setDaemon(True)
        thread.start()
        download_threads.append(thread)

    # Keep the queue filled
    dataset_idx = 0
    urls_processed = 0

    try:
        while MAX_DOWNLOADS is None or urls_processed < MAX_DOWNLOADS:
            if url_queue.qsize() < 10:
                # fetch data
                urls = datasets[dataset_idx].get_image_urls(50)
                for url in urls:
                    if urls_processed >= MAX_DOWNLOADS:
                        break

                    url_queue.put(url)
                    urls_processed += 1

                dataset_idx = (dataset_idx + 1) % len(datasets)
            else:
                time.sleep(0.5)
    finally:
        url_queue.join()
        logger.info("==================")
        logger.info("Finished downloading icons. Storing dataset states")
        for dataset in datasets:
            dataset.save_state()
