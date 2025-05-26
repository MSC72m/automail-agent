from abc import ABC, abstractmethod
from typing import List

class IProfileManager(ABC):
    @abstractmethod
    def get_available_profiles(self) -> List[str]:
        pass