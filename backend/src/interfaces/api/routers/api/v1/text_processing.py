import time

from ahocorasick import Automaton
from fastapi import APIRouter, Depends

from src.application.services.text_processing import TextProcessingService
from src.infrastructure.schemas.text_processing import TextRequest
from src.interfaces.api.dependencies.automaton import get_automaton

router = APIRouter()


@router.post("/find_medications/")
async def find_medications(
    request: TextRequest,
    service: TextProcessingService = Depends(),
    automaton: Automaton = Depends(get_automaton),
):

    return await service.find_medications(
        automaton, request.text, fuzzy=request.fuzzy
    )
