from abc import ABC, abstractmethod

from src.schemas.email import EmailInput

class IMailer(ABC):
    @abstractmethod
    def send_email(self, email_data: EmailInput) -> bool:
        pass

    @abstractmethod
    def connect_to_gmail(self) -> bool:
        pass
    