from abc import ABC, abstractmethod
from typing import Optional, List


class IBrowserFinder(ABC):
    @abstractmethod
    def find_browser_executable(self) -> Optional[str]:
        pass
    
    @abstractmethod
    def get_possible_paths(self) -> Optional[List[str]]:
        pass