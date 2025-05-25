from abc import ABC, abstractmethod
from typing import Optional

from src.schemas.enums import OSType


class BrowserInstanceFinder(ABC):
    def __init__(self, os_type: OSType):
        self.os_type = os_type

    @abstractmethod
    def find_instance(self) -> Optional[str]:
        pass
