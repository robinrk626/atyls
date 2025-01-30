from pydantic import BaseModel, Field
from typing import Optional

class ScraperSettings(BaseModel):
  maxPages: Optional[int] = Field(default=10, ge=1)
  proxy: Optional[str] = None