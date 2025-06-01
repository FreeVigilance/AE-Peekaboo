import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TextRequest(BaseModel):
    text: str
    fuzzy: bool = False


class Drug(BaseModel):
    id: uuid.UUID
    trade_name: str

    model_config = ConfigDict(from_attributes=True)


class DrugTable(BaseModel):
    trade_name: str
    inn: str | None = None
    obligation: str | None = None
    source_countries: str | None = None
    receiver: str | None = None
    deadline_to_submit: str | date | None = None
    format: str | None = None
    other_procedures: str | None = None
    type_of_event: str | None = None
    valid_start_date: datetime | None = None
    valid_end_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
