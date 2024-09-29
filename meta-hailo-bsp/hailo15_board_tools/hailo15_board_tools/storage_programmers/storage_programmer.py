from abc import ABC, abstractmethod
import logging
import sys

logger = logging.getLogger("BURN_STORAGE_HAILO15_LOGGER")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


class StorageProgrammer(ABC):

    @abstractmethod
    def write(self, address, buffer_data):
        pass

    @abstractmethod
    def read(self, address, length):
        pass

    @abstractmethod
    def erase(self, address, length):
        pass

    @abstractmethod
    def identify(self):
        pass

    @abstractmethod
    def open_interface(self):
        pass

    def close(self):
        pass
