from abc import ABC, abstractmethod
from typing import Optional, List
from playwright.async_api import Page


class IBrowserLauncher(ABC):
    @abstractmethod
    def launch(self, profile_name: str = "Default", debug_port: Optional[int] = None, additional_args: Optional[List[str]] = None) -> bool:
        pass

    @abstractmethod
    def get_page(self) -> Optional[Page]:
        pass
    
