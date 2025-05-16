import uuid
from datetime import date

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
    obligation: str | None
    source_countries: str | None
    receiver: str | None
    deadline_to_submit: str | date | None
    format: str | None
    other_procedures: str | None
    type_of_event: str | None

    model_config = ConfigDict(from_attributes=True)
