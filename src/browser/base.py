from abc import ABC, abstractmethod
from typing import Optional
from playwright.async_api import Page

from src.schemas.enums import OSType

class BrowserInstanceFinder(ABC):
    @abstractmethod
    def find_instance(self) -> Optional[str]:
        pass

class BrowserLauncher(ABC):
    @abstractmethod
    async def launch(self, url: str) -> Optional[Page]:
        pass
