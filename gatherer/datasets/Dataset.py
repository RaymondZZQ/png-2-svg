from abc import ABC, abstractmethod
import logging
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

PICKLE_DIRECTORY = Path("datasets/state")
if not PICKLE_DIRECTORY.exists():
    PICKLE_DIRECTORY.mkdir()


class Dataset(ABC):
    def __init__(self, name):
        super(Dataset, self).__init__()
        self.name = name
        self.restore_state()

    @abstractmethod
    def get_image_urls(self, amount):
        pass

    @abstractmethod
    def __getstate__(self):
        pass

    def __setstate__(self, state):
        # Restore instance attributes
        self.__dict__.update(state)

    def _log(self, msg):
        logger.info('[%s] %s', self.name, msg)

    def restore_state(self):
        path = PICKLE_DIRECTORY / '{}.pickle'.format(self.name)

        if not path.exists():
            return

        self._log('Restoring state')

        with path.open('rb') as f:
            self.__setstate__(pickle.load(f))

    def save_state(self):
        self._log('Saving state')
        state = self.__getstate__()

        path = PICKLE_DIRECTORY / '{}.pickle'.format(self.name)
        with path.open('wb') as f:
            pickle.dump(state, f, pickle.HIGHEST_PROTOCOL)
