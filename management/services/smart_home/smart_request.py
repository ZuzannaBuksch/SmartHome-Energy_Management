from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SmartHomeRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "token": "ghp_3627292^%736382",
            }
        }
