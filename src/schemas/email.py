from pydantic import BaseModel, Field
from typing import Optional, List


class EmailInput(BaseModel):
    to: str = Field(
        ...,
        description="The recipient email address"
    )
    subject: str = Field(
        ...,
        description="The email subject line"
    )
    body: str = Field(
        ...,
        description="The email body content"
    )
    cc: Optional[List[str]] = Field(
        default=None,
        description="List of CC email addresses"
    )
    bcc: Optional[List[str]] = Field(
        default=None,
        description="List of BCC email addresses"
    )
    attachments: Optional[List[str]] = Field(
        default=None,
        description="List of file paths to attach"
    ) 